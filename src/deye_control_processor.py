"""Optional SG03LP1 transaction processor using the existing MQTT client and bus.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy at http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations.
"""

import itertools
import json
import math
import os
from pathlib import Path
import queue
import threading
import time

from deye_control_core import ControlError, Engine, ID_PATTERN
from deye_control_transport import StrictModbus


class ControlProcessor:
    def __init__(self, engine, mqtt, logger_index):
        self.engine, self.mqtt, self.logger_index = engine, mqtt, logger_index
        self.requests = queue.PriorityQueue(maxsize=64)
        self.sequence = itertools.count()
        self.stop_event = threading.Event()
        self.rpc_thread = threading.Thread(target=self._run_requests, name="control-rpc", daemon=True)
        self.publisher = threading.Thread(target=self._publish_state, name="control-state", daemon=True)

    def start(self):
        self.mqtt.subscribe_exact_handler(self.logger_index, "control/request", self.handle_message)
        self.rpc_thread.start()
        self.publisher.start()

    def handle_message(self, client, userdata, msg):
        # Never execute device work or block on publishing from Paho's callback.
        if msg.retain or len(msg.payload) > 16384:
            return
        try:
            request = json.loads(msg.payload, parse_constant=lambda _: (_ for _ in ()).throw(ValueError()))
            if not isinstance(request, dict) or request.get("schema", 1) != 1:
                return
            request_id = request.get("request_id")
            if not isinstance(request_id, str) or not ID_PATTERN.fullmatch(request_id):
                return
            body = request.get("body", {})
            off = (
                request.get("op") == "submit"
                and isinstance(body, dict)
                and (
                    body.get("action") == "grid_off"
                    or (body.get("action") == "set_current" and type(body.get("ampere")) is int and body["ampere"] == 0)
                )
            )
            # Reserve eight queue slots for protective cuts.
            if not off and self.requests.qsize() >= 56:
                return
            self.requests.put_nowait((0 if off else 1, next(self.sequence), request))
        except (ValueError, TypeError, queue.Full):
            return

    def _publish(self, suffix, value):
        try:
            return self.mqtt.publish_control(self.logger_index, suffix, json.dumps(value, allow_nan=False))
        except Exception:
            # Publication failure never interrupts device execution or OFF.
            return False

    def dispatch(self, request):
        operation, body = request.get("op"), request.get("body", {})
        if not isinstance(body, dict):
            raise ControlError("invalid_body", 400)
        if operation == "status":
            return self.engine.status()
        if operation == "get":
            return self.engine.get(body.get("id"))
        if operation == "preview":
            return self.engine.preview(body)
        if operation == "submit":
            # IDs and deadlines must originate at the publisher, not reception:
            # a QoS 1 redelivery must neither become a new order nor gain time.
            if "id" not in body or "expires_at" not in body:
                raise ControlError("id_and_expiry_required", 400)
            return self.engine.submit(body)
        if operation == "session":
            return self._session(request)
        raise ControlError("unknown_operation", 400)

    def _session(self, request):
        request_id = request["request_id"]
        with self.engine.mutex:
            saved = self.engine.journal.rpc_requests.get(request_id)
            if saved:
                if saved["request"] != request:
                    raise ControlError("id_conflict", 409)
                return saved["result"]  # Never renew authority on replay.
            now = time.time()
            expires = request.get("expires_at")
            if type(expires) not in (float, int) or not math.isfinite(expires) or not now < expires <= now + 60:
                raise ControlError("invalid_expiry", 400)
            entries = self.engine.journal.rpc_requests
            for key in list(entries):
                if entries[key]["request"]["expires_at"] < now - 300:
                    del entries[key]
            if len(entries) >= 128:
                raise ControlError("session_history_full", 503)
            # Crash before the final save leaves this request consumed but never
            # restores a manual session when the process restarts.
            entries[request_id] = {"request": request, "result": {"manual_session_until": 0}}
            self.engine.journal.save()
            result = self.engine.open_session(request.get("body"))
            entries[request_id]["result"] = result
            self.engine.journal.save()
            return result

    def _run_requests(self):
        while not self.stop_event.is_set():
            try:
                _, _, request = self.requests.get(timeout=0.2)
            except queue.Empty:
                continue
            response = {"schema": 1, "request_id": request["request_id"], "op": request.get("op")}
            try:
                response.update(ok=True, result=self.dispatch(request))
            except ControlError as error:
                response.update(ok=False, error=error.code, status=error.status)
            except Exception:
                response.update(ok=False, error="control_unavailable", status=503)
            self._publish("control/result", response)

    def _publish_state(self):
        previous, previous_commands, last_sent = None, {}, 0
        while not self.stop_event.wait(0.25):
            try:
                state = self.engine.status()
                key = json.dumps({k: v for k, v in state.items() if k != "sample_age_seconds"}, sort_keys=True)
                if key != previous or time.monotonic() - last_sent >= 10:
                    if self._publish("control/state", state):
                        previous, last_sent = key, time.monotonic()
                for command in state["commands"]:
                    marker = (command["state"], command.get("completed_at"), command.get("resolved_by"))
                    if previous_commands.get(command["id"]) != marker:
                        if self._publish("control/result", {"schema": 1, "event": "command", "command": command}):
                            previous_commands[command["id"]] = marker
                current_ids = {command["id"] for command in state["commands"]}
                previous_commands = {key: value for key, value in previous_commands.items() if key in current_ids}
            except Exception:
                # State RPC remains independent from result publication.
                continue

    def record_frame(self, regs, started, completed, failure=None):
        self.engine.record_frame(regs, started, completed, failure)

    def off_pending(self):
        return self.engine.off_pending()

    def close(self):
        self.stop_event.set()
        for thread in (self.rpc_thread, self.publisher):
            if thread.is_alive():
                thread.join(timeout=3)
        self.engine.close()


def create_control(config, logger_config, mqtt, modbus, budget=None, unit_id=None):
    if os.getenv("DEYE_FEATURE_LOCAL_CONTROL", "false") != "true":
        return None
    for name in ("DEYE_FEATURE_BATTERY_SETTINGS", "DEYE_FEATURE_WORKMODE"):
        if os.getenv(name, "false") == "true":
            raise ValueError("Transactional control conflicts with scalar battery/workmode control")
    index = logger_config.index

    def setting(name, default=None):
        return os.getenv(f"DEYE_CONTROL_{index}_{name}", os.getenv(f"DEYE_CONTROL_{name}", default))

    if setting("MODEL") != "sg03lp1":
        raise ValueError("Local control requires an explicit supported model: sg03lp1")
    groups = {"deye_hybrid", "deye_hybrid_battery", "deye_hybrid_timeofuse"}
    if not groups <= set(config.metric_groups):
        raise ValueError("Local control requires hybrid, battery and timeofuse metric groups")
    root = setting("STATE_DIR")
    if not root or not Path(root).is_absolute():
        raise ValueError("Local control requires a persistent absolute STATE_DIR")
    state_dir = Path(root) if index == 0 else Path(root) / f"logger-{index}"
    engine = Engine(
        StrictModbus(modbus, unit_id),
        state_dir,
        writes_enabled=setting("WRITES_ENABLED", "false") == "true",
        max_ampere=int(setting("MAX_CURRENT", "65")),
        authority=setting("AUTHORITY", "manual"),
        budget=budget,
    )
    processor = ControlProcessor(engine, mqtt, index)
    try:
        processor.start()
    except Exception:
        processor.close()
        raise
    return processor
