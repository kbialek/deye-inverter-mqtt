# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

"""Typed, durable control service. No MQTT, cloud credentials or HA imports."""

from __future__ import annotations

import contextlib
import copy
import fcntl
import hashlib
import heapq
import json
import math
import os
from pathlib import Path
import re
import threading
import time
import uuid

MODES = {"SELLING_FIRST": 0, "ZERO_EXPORT_TO_LOAD": 1, "ZERO_EXPORT_TO_CT": 2}
CONFIG_REGS = (210, 211, 230, 232, 244, 247, 248, *range(250, 280))
REQUIRED_REGS = (150, 169, 183, 184, 190, 194, *CONFIG_REGS)
ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{8,80}$")
TERMINAL = {"confirmed", "failed", "expired", "cancelled", "uncertain"}


class ControlError(Exception):
    def __init__(self, code, status=409):
        super().__init__(code)
        self.code, self.status = code, status


def normalize(body, now=None, max_ampere=65):
    """Validate typed intent without performing device I/O."""
    now = time.time() if now is None else now
    if not isinstance(body, dict):
        raise ControlError("invalid_request", 400)
    allowed = {"id", "action", "ampere", "work_mode", "expected_revision", "expires_at"}
    if set(body) - allowed:
        raise ControlError("unknown_field", 400)
    request = copy.deepcopy(body)
    request.setdefault("id", uuid.uuid4().hex)
    if not isinstance(request["id"], str) or not ID_PATTERN.fullmatch(request["id"]):
        raise ControlError("invalid_id", 400)
    action = request.get("action")
    if action not in {"grid_on", "grid_off", "set_current", "set_mode"}:
        raise ControlError("invalid_action", 400)
    if action in {"grid_on", "set_current"}:
        amp = request.get("ampere")
        if type(amp) is not int or not 0 <= amp <= max_ampere or (action == "grid_on" and amp == 0):
            raise ControlError("ampere_out_of_range", 400)
        if action == "set_current" and amp == 0:
            request["action"] = "grid_off"
            request.pop("ampere")
    elif "ampere" in request:
        raise ControlError("unexpected_ampere", 400)
    if "work_mode" in request:
        if request["work_mode"] not in MODES or action not in {"grid_on", "set_mode"}:
            raise ControlError("invalid_work_mode", 400)
    if action == "set_mode" and "work_mode" not in request:
        raise ControlError("missing_work_mode", 400)
    if request["action"] != "grid_off":
        rev = request.get("expected_revision")
        if not isinstance(rev, str) or not re.fullmatch(r"[0-9a-f]{64}", rev):
            raise ControlError("expected_revision_required", 400)
    expires = request.setdefault("expires_at", now + 30)
    if type(expires) not in (int, float) or not math.isfinite(expires) or not now < expires <= now + 60:
        raise ControlError("invalid_expiry", 400)
    return request


def configuration_revision(regs):
    data = [[reg, regs[reg]] for reg in CONFIG_REGS]
    return hashlib.sha256(json.dumps(data, separators=(",", ":")).encode()).hexdigest()


def decode(regs, started, completed):
    if not all(reg in regs for reg in REQUIRED_REGS):
        raise ControlError("incomplete_frame", 503)

    def signed(value):
        return value - 65536 if value & 0x8000 else value

    return {
        "source": "local",
        "read_started_at": started,
        "measured_at": completed,
        "revision": configuration_revision(regs),
        "grid_connected": {0: False, 1: True}.get(regs[194]),
        "grid_voltage_v": round(regs[150] * 0.1, 1),
        "grid_power_w": signed(regs[169]),
        "battery_soc_pct": regs[184],
        "battery_voltage_v": round(regs[183] * 0.01, 2),
        "battery_power_w": signed(regs[190]),
        "grid_charge_ampere": regs[230],
        "grid_charge_enabled": bool(regs[232] & 1),
        "work_mode": next((name for name, value in MODES.items() if value == regs[244]), None),
        "maximum_charge_ampere": regs[210],
        "maximum_discharge_ampere": regs[211],
        "solar_sell_enabled": bool(regs[247] & 1),
        "tou_global": regs[248],
    }


class Journal:
    """Private durable intent; one bridge process owns the state directory."""

    def __init__(self, directory):
        self.directory = Path(directory)
        self.directory.mkdir(mode=0o700, parents=True, exist_ok=True)
        os.chmod(self.directory, 0o700)
        self.lockfile = (self.directory / "executor.lock").open("a+")
        os.chmod(self.lockfile.name, 0o600)
        try:
            fcntl.flock(self.lockfile, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            self.lockfile.close()
            raise
        self.path = self.directory / "commands.json"
        self.records = {}
        self.rpc_requests = {}
        if self.path.exists():
            data = json.loads(self.path.read_text())
            if data.get("schema") != 1 or not isinstance(data.get("commands"), dict):
                raise ValueError("invalid_control_journal")
            self.records = data["commands"]
            self.rpc_requests = data.get("rpc_requests", {})
        recovered = False
        for record in self.records.values():
            if record["state"] not in TERMINAL:
                record.update(
                    state="uncertain" if record.get("write_attempted") else "cancelled",
                    error="executor_restarted",
                    completed_at=time.time(),
                )
                recovered = True
        if recovered:
            self.save()

    def save(self):
        temp = self.path.with_suffix(".new")
        fd = os.open(temp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, "w") as output:
            json.dump(
                {"schema": 1, "commands": self.records, "rpc_requests": self.rpc_requests},
                output,
                separators=(",", ":"),
            )
            output.flush()
            os.fsync(output.fileno())
        os.replace(temp, self.path)
        fd = os.open(self.directory, os.O_DIRECTORY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)

    def make_room(self):
        # Never discard unresolved uncertainty or an active request.
        resolved = [
            key
            for key, value in self.records.items()
            if value["state"] in TERMINAL and (value["state"] != "uncertain" or value.get("resolved_by"))
        ]
        while len(self.records) >= 250 and resolved:
            del self.records[resolved.pop(0)]
        if len(self.records) >= 250:
            raise ControlError("journal_capacity", 503)

    def close(self):
        self.lockfile.close()


class Engine:
    def __init__(
        self, modbus, state_dir, writes_enabled=False, budget=None, start_worker=True, max_ampere=65, authority="manual"
    ):
        self.modbus = modbus
        if type(max_ampere) is not int or not 1 <= max_ampere <= 240:
            raise ValueError("invalid_current_cap")
        if authority not in ("manual", "service"):
            raise ValueError("invalid_authority")
        self.journal = Journal(state_dir)
        self.max_ampere = max_ampere
        self.authority = authority
        self.read_seq = 0
        self.writes_enabled = writes_enabled
        self.budget = budget or (lambda seconds: contextlib.nullcontext())
        self.mutex = threading.RLock()
        self.condition = threading.Condition(self.mutex)
        self.frames = None
        self.frame_error = "waiting_for_acquisition"
        self.queue = []
        self.sequence = 0
        self.off_generation = 0
        self.session_until = 0.0
        self.boot_id = uuid.uuid4().hex
        self.stop_event = threading.Event()
        self.worker = threading.Thread(target=self._run, name="deye-local-control", daemon=True)
        if start_worker:
            self.worker.start()

    def record_frame(self, raw_regs, started, completed, failure=None):
        # Called by the existing acquisition. No network or storage work here.
        try:
            regs = {
                key: int.from_bytes(value, "big") if not isinstance(value, int) else value
                for key, value in raw_regs.items()
                if key in REQUIRED_REGS
            }
            frame = None if failure else decode(regs, started, completed)
            error = failure
        except Exception:
            frame, error = None, "incomplete_frame"
        with self.mutex:
            self.read_seq += 1
            if frame:
                self.frames = frame
            self.frame_error = error

    def status(self):
        with self.mutex:
            now = time.time()
            sample = copy.deepcopy(self.frames)
            age = now - sample["read_started_at"] if sample else None
            valid = (
                sample is not None
                and not self.frame_error
                and 0 <= age <= 90
                and sample["read_started_at"] <= sample["measured_at"] <= now
            )
            unresolved = [
                record["id"]
                for record in self.journal.records.values()
                if record["state"] == "uncertain" and not record.get("resolved_by")
            ]
            return {
                "schema": 1,
                "version": "0.2.0",
                "model": "SUN-5K-SG03LP1",
                "boot_id": self.boot_id,
                "read_seq": self.read_seq,
                "authority": self.authority,
                "max_ampere": self.max_ampere,
                "available": valid,
                "sample_age_seconds": age,
                "error": self.frame_error if self.frame_error else (None if valid else "stale_frame"),
                "writes_enabled": self.writes_enabled,
                "manual_session_until": self.session_until,
                "manual_session_active": self.session_until > now,
                "uncertain_commands": unresolved,
                "sample": sample,
                "commands": copy.deepcopy(list(self.journal.records.values())[-20:]),
            }

    def open_session(self, body):
        if self.authority != "manual":
            raise ControlError("manual_sessions_disabled", 423)
        if not self.writes_enabled:
            raise ControlError("writes_disabled", 423)
        if body != {"exclusive_window_confirmed": True}:
            raise ControlError("exclusive_window_confirmation_required", 400)
        with self.mutex:
            self.session_until = time.time() + 300
            return {"manual_session_until": self.session_until}

    def preview(self, body):
        request = normalize(body, max_ampere=self.max_ampere)
        state = self.status()
        if not state["available"]:
            raise ControlError("telemetry_unavailable", 503)
        if request["action"] != "grid_off" and request["expected_revision"] != state["sample"]["revision"]:
            raise ControlError("configuration_changed", 409)
        return {
            "validated": True,
            "writes_performed": False,
            "request": request,
            "requires_manual_session": self.authority == "manual",
            "writes_enabled": self.writes_enabled,
        }

    def submit(self, body):
        # An exact duplicate returns its original result even after expiry/restart.
        with self.condition:
            original = self.journal.records.get(body.get("id")) if isinstance(body, dict) else None
            if original:
                if original["submitted"] != body:
                    raise ControlError("id_conflict", 409)
                return copy.deepcopy(original)
            request = normalize(body, max_ampere=self.max_ampere)
            if not self.writes_enabled:
                raise ControlError("writes_disabled", 423)
            if self.authority == "manual" and self.session_until <= time.time():
                raise ControlError("manual_session_required", 423)
            if request["action"] != "grid_off" and self.status()["uncertain_commands"]:
                raise ControlError("uncertain_previous_command", 409)
            if len(self.queue) >= 10 and request["action"] != "grid_off":
                raise ControlError("queue_full", 503)
            self.journal.make_room()
            if request["action"] == "grid_off":
                self.off_generation += 1
                for _, _, queued_id in self.queue:
                    queued = self.journal.records[queued_id]
                    if queued["action"] != "grid_off":
                        queued.update(state="cancelled", error="superseded_by_off", completed_at=time.time())
                self.queue = [entry for entry in self.queue if self.journal.records[entry[2]]["state"] == "received"]
                heapq.heapify(self.queue)
            record = {
                "id": request["id"],
                "action": request["action"],
                "request": request,
                "submitted": copy.deepcopy(body),
                "generation": self.off_generation,
                "state": "received",
                "received_at": time.time(),
                "write_attempted": False,
                "registers_confirmed": False,
                "physical_confirmed": False,
            }
            self.journal.records[record["id"]] = record
            self.journal.save()
            self.sequence += 1
            heapq.heappush(self.queue, (0 if request["action"] == "grid_off" else 1, self.sequence, record["id"]))
            self.condition.notify()
            return copy.deepcopy(record)

    def get(self, command_id):
        with self.mutex:
            record = self.journal.records.get(command_id)
            if not record:
                raise ControlError("command_not_found", 404)
            return copy.deepcopy(record)

    def off_pending(self):
        with self.mutex:
            return any(
                self.journal.records[key]["state"] == "received" and self.journal.records[key]["action"] == "grid_off"
                for _, _, key in self.queue
            )

    def _run(self):
        while not self.stop_event.is_set():
            with self.condition:
                self.condition.wait_for(lambda: self.queue or self.stop_event.is_set(), timeout=1)
                if self.stop_event.is_set():
                    return
                if not self.queue:
                    continue
                _, _, key = heapq.heappop(self.queue)
            self.execute(key)

    def _update(self, record, **fields):
        with self.mutex:
            record.update(fields)
            self.journal.save()

    def _read(self):
        started, regs = time.time(), {}
        for first, last in ((150, 213), (214, 249), (250, 279)):
            result = self.modbus.read_registers(first, last)
            if not result or any(reg not in result for reg in range(first, last + 1)):
                raise ControlError("readback_unavailable", 503)
            regs.update(
                {
                    key: int.from_bytes(value, "big") if not isinstance(value, int) else value
                    for key, value in result.items()
                }
            )
        return regs, started, time.time()

    def _check_authority(self, record):
        if self.authority == "manual" and self.session_until <= time.time():
            raise ControlError("manual_session_expired", 423)
        if time.time() >= record["request"]["expires_at"]:
            raise ControlError("command_expired", 409)
        if record["action"] != "grid_off" and record["generation"] != self.off_generation:
            raise ControlError("superseded_by_off", 409)
        if self.stop_event.is_set():
            raise ControlError("executor_stopping", 503)

    def _write(self, record, address, value):
        with self.mutex:
            self._check_authority(record)
            self._update(record, write_attempted=True)
            self.frame_error = "control_write_unconfirmed"
        if not self.modbus.write_register_uint(address, value):
            raise ControlError("write_result_unknown", 503)

    def _confirm(self, record, desired, off):
        # A device can return an invalid first read while applying settings.
        # Retry only reads; never repeat any write or relax frame validation.
        for attempt, delay in enumerate((0, 0.25, 0.75, 1.5), start=1):
            if delay:
                if self.off_pending() and not off:
                    raise ControlError("superseded_by_off", 409)
                time.sleep(delay)
            self._update(record, readback_attempts=attempt)
            try:
                if off:
                    after = self.modbus.read_registers(230, 232)
                    if not after or any(key not in after for key in (230, 232)):
                        raise ControlError("readback_unavailable", 503)
                    after = {
                        key: int.from_bytes(value, "big") if not isinstance(value, int) else value
                        for key, value in after.items()
                    }
                    after[244] = None
                    completed = time.time()
                    confirmation = {
                        "source": "local",
                        "measured_at": completed,
                        "grid_charge_ampere": after[230],
                        "grid_charge_enabled": bool(after[232] & 1),
                    }
                else:
                    after, started, completed = self._read()
                    confirmation = decode(after, started, completed)
                if any(after[address] != value for address, value in desired.items()):
                    raise ControlError("registers_disagree", 409)
                if not off:
                    self.record_frame(after, started, completed)
                return completed, confirmation
            except ControlError as error:
                if error.code not in ("readback_unavailable", "registers_disagree"):
                    raise
                self._update(
                    record,
                    last_readback_error=error.code,
                    last_readback_response=getattr(self.modbus, "last_read_error", None),
                )
                if attempt == 4:
                    raise

    def execute(self, key):
        record = self.journal.records[key]
        if record["state"] in TERMINAL:
            return
        locked = False
        try:
            self._check_authority(record)
            self._update(record, state="executing", started_at=time.time())
            with self.budget(40):
                locked = self.modbus.transaction_lock.acquire(
                    timeout=max(0.0, min(30.0, record["request"]["expires_at"] - time.time()))
                )
                if not locked:
                    raise ControlError("bus_busy", 503)
                self._check_authority(record)
                request = record["request"]
                off = record["action"] == "grid_off"
                # OFF needs only its own registers: unavailable TOU/battery
                # telemetry must not prevent a protective cut.
                if off:
                    regs = self.modbus.read_registers(230, 232)
                    if not regs or any(key not in regs for key in (230, 232)):
                        raise ControlError("readback_unavailable", 503)
                    regs = {
                        key: int.from_bytes(value, "big") if not isinstance(value, int) else value
                        for key, value in regs.items()
                    }
                    regs[244] = None  # OFF never reads or writes work mode.
                else:
                    regs, started, completed = self._read()
                    current = decode(regs, started, completed)
                if not off:
                    if request["expected_revision"] != current["revision"]:
                        raise ControlError("configuration_changed", 409)
                    if (
                        current["grid_connected"] is not True
                        or not 40 <= current["battery_voltage_v"] <= 60
                        or not 0 <= current["battery_soc_pct"] <= 100
                    ):
                        raise ControlError("invalid_physical_preconditions", 409)
                    if "ampere" in request and request["ampere"] > current["maximum_charge_ampere"]:
                        raise ControlError("battery_limit_exceeded", 409)
                    if record["action"] == "grid_on" and current["battery_soc_pct"] >= 100:
                        raise ControlError("battery_full", 409)
                desired = {230: regs[230], 232: regs[232], 244: regs[244]}
                if off:
                    desired[232] &= ~1
                    desired[230] = 0
                else:
                    if "work_mode" in request:
                        desired[244] = MODES[request["work_mode"]]
                    if "ampere" in request:
                        desired[230] = request["ampere"]
                    if record["action"] == "grid_on":
                        desired[232] |= 1
                # Disable before a work-mode change, then restore the requested bit.
                if off or (desired[244] != regs[244] and regs[232] & 1):
                    if regs[232] & 1:
                        self._write(record, 232, regs[232] & ~1)
                        regs[232] &= ~1
                for address in (244, 230, 232):
                    if regs[address] != desired[address]:
                        self._write(record, address, desired[address])
                        regs[address] = desired[address]
                completed, confirmation = self._confirm(record, desired, off)
                self._update(
                    record,
                    state="confirmed",
                    completed_at=completed,
                    registers_confirmed=True,
                    confirmed_configuration=confirmation,
                )
                if off:
                    with self.mutex:
                        for other in self.journal.records.values():
                            if other["state"] == "uncertain" and not other.get("resolved_by"):
                                other["resolved_by"] = record["id"]
                        self.journal.save()
        except Exception as error:
            code = error.code if isinstance(error, ControlError) else "executor_error"
            uncertain = record["write_attempted"]
            state = "uncertain" if uncertain else ("expired" if code == "command_expired" else "failed")
            self._update(record, state=state, error=code, completed_at=time.time())
        finally:
            if locked:
                self.modbus.transaction_lock.release()
            if record["write_attempted"]:
                self.modbus.request_read(confirmation=True)

    def close(self):
        self.stop_event.set()
        with self.condition:
            self.condition.notify_all()
        if self.worker.is_alive():
            self.worker.join(timeout=45)
        # Keep exclusive ownership until an in-flight worker really stops.
        if not self.worker.is_alive():
            self.journal.close()
