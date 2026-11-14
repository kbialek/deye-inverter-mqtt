import copy
import json
from pathlib import Path
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

from deye_control_core import ControlError, Engine, configuration_revision, decode, normalize
from deye_control_transport import StrictModbus, frame


def sample_regs():
    regs = {address: 0 for address in range(150, 280)}
    regs.update(
        {
            150: 2275,
            169: 71,
            183: 4940,
            184: 41,
            190: 65536 - 117,
            194: 1,
            210: 70,
            211: 90,
            230: 0,
            232: 4,
            244: 2,
            247: 1,
            248: 255,
        }
    )
    for address in range(250, 280):
        regs[address] = 4 if address >= 274 else 40
    return regs


class FakeModbus:
    def __init__(self):
        self.regs = sample_regs()
        self.transaction_lock = threading.RLock()
        self.read_requested = threading.Event()
        self.confirmation_read_requested = threading.Event()
        self.modbus_id = 1
        self.writes = []
        self.fail_write = False
        self.partial_read = False
        self.tou_missing = False
        self.on_read = None

    def request_read(self, confirmation=False):
        self.read_requested.set()
        if confirmation:
            self.confirmation_read_requested.set()

    def read_registers(self, first, last):
        if self.on_read:
            callback, self.on_read = self.on_read, None
            callback()
        if self.partial_read or (self.tou_missing and first == 250):
            return {}
        return {key: value.to_bytes(2, "big") for key, value in self.regs.items() if first <= key <= last}

    def write_register_uint(self, key, value):
        self.writes.append((key, value))
        self.regs[key] = value  # lost ACK can still mean applied
        return not self.fail_write


class EngineTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.bus = FakeModbus()
        self.engine = Engine(self.bus, self.directory.name, writes_enabled=True, start_worker=False)
        self.engine.record_frame(self.bus.regs, time.time() - 1, time.time())
        self.engine.open_session({"exclusive_window_confirmed": True})

    def tearDown(self):
        self.engine.close()
        self.directory.cleanup()

    def body(self, action="grid_on", **fields):
        request = {
            "id": "command_0001",
            "action": action,
            "expires_at": time.time() + 30,
            "expected_revision": configuration_revision(self.bus.regs),
        }
        if action in {"grid_on", "set_current"}:
            request["ampere"] = 10
        request.update(fields)
        return request

    def execute(self, body):
        record = self.engine.submit(body)
        self.engine.execute(record["id"])
        return self.engine.get(record["id"])

    def test_real_decoding_uses_installed_monophase_map(self):
        decoded = decode(self.bus.regs, 1, 2)
        self.assertEqual(
            (decoded["battery_soc_pct"], decoded["battery_voltage_v"], decoded["battery_power_w"]), (41, 49.4, -117)
        )

    def test_on_preserves_bitfields_and_limits_and_confirms_parameters(self):
        original = copy.deepcopy(self.bus.regs)
        result = self.execute(self.body())
        self.assertEqual(self.bus.writes, [(230, 10), (232, 5)])
        self.assertEqual(result["state"], "confirmed")
        self.assertTrue(result["registers_confirmed"])
        self.assertFalse(result["physical_confirmed"])
        self.assertEqual(
            {k: v for k, v in self.bus.regs.items() if k not in (230, 232)},
            {k: v for k, v in original.items() if k not in (230, 232)},
        )

    def test_off_clears_only_grid_bit_before_current_and_works_without_tou(self):
        self.bus.regs.update({230: 30, 232: 7})
        self.bus.tou_missing = True
        result = self.execute(self.body("grid_off"))
        self.assertEqual(self.bus.writes, [(232, 6), (230, 0)])
        self.assertEqual(result["state"], "confirmed")

    def test_set_zero_means_protective_off(self):
        self.bus.regs.update({230: 30, 232: 5})
        result = self.execute(self.body("set_current", ampere=0))
        self.assertEqual(result["action"], "grid_off")
        self.assertEqual(self.bus.writes, [(232, 4), (230, 0)])

    def test_mode_change_cuts_before_change_then_restores_permission(self):
        self.bus.regs.update({230: 10, 232: 5})
        result = self.execute(self.body("set_mode", work_mode="ZERO_EXPORT_TO_LOAD"))
        self.assertEqual(self.bus.writes, [(232, 4), (244, 1), (232, 5)])
        self.assertEqual(result["state"], "confirmed")

    def test_duplicate_does_not_write_twice_even_after_expiry(self):
        body = self.body()
        first = self.execute(body)
        with patch("deye_control_core.time.time", return_value=body["expires_at"] + 1):
            self.assertEqual(self.engine.submit(body), first)
        self.assertEqual(len(self.bus.writes), 2)

    def test_changed_payload_cannot_reuse_id(self):
        body = self.body()
        self.execute(body)
        with self.assertRaisesRegex(ControlError, "id_conflict"):
            self.engine.submit({**body, "ampere": 15})

    def test_external_change_after_preview_prevents_every_write(self):
        body = self.body()
        self.engine.preview(body)
        self.bus.regs[274] ^= 1
        result = self.execute(body)
        self.assertEqual(result["error"], "configuration_changed")
        self.assertFalse(self.bus.writes)

    def test_lost_ack_is_uncertain_and_does_not_retry(self):
        self.bus.fail_write = True
        result = self.execute(self.body())
        self.assertEqual(result["state"], "uncertain")
        self.assertEqual(self.bus.writes, [(230, 10)])
        with self.assertRaisesRegex(ControlError, "uncertain_previous_command"):
            self.engine.submit(self.body(id="command_0002"))
        self.bus.fail_write = False
        result = self.execute(self.body("grid_off", id="command_0003"))
        self.assertTrue(result["registers_confirmed"])
        self.assertFalse(self.engine.status()["uncertain_commands"])

    def test_transient_post_write_read_failure_retries_reads_without_rewriting(self):
        original_read, original_write = self.bus.read_registers, self.bus.write_register_uint
        pending = [False]

        def write(key, value):
            pending[0] = True
            return original_write(key, value)

        def read(first, last):
            if pending[0]:
                pending[0] = False
                return {}
            return original_read(first, last)

        self.bus.write_register_uint, self.bus.read_registers = write, read
        result = self.execute(self.body())
        self.assertEqual(result["state"], "confirmed")
        self.assertEqual(result["readback_attempts"], 2)
        self.assertEqual(self.bus.writes, [(230, 10), (232, 5)])

    def test_permanent_post_write_read_failure_stays_uncertain_without_rewriting(self):
        original_write = self.bus.write_register_uint

        def write(key, value):
            self.bus.partial_read = True
            return original_write(key, value)

        self.bus.write_register_uint = write
        with patch("deye_control_core.time.sleep"):
            result = self.execute(self.body())
        self.assertEqual(result["state"], "uncertain")
        self.assertEqual(result["readback_attempts"], 4)
        self.assertEqual(self.bus.writes, [(230, 10), (232, 5)])

    def test_off_cancels_queued_on(self):
        first = self.engine.submit(self.body())
        self.engine.submit(self.body("grid_off", id="command_0002"))
        self.engine.execute(first["id"])
        self.assertEqual(self.engine.get(first["id"])["state"], "cancelled")
        self.assertFalse(self.bus.writes)

    def test_full_positive_queue_does_not_block_off(self):
        for n in range(10):
            self.engine.submit(self.body(id="queued_" + str(n).zfill(8)))
        record = self.engine.submit(self.body("grid_off", id="emergency_off"))
        self.assertEqual(record["state"], "received")
        self.assertEqual(len(self.engine.queue), 1)

    def test_off_received_during_positive_pre_read_prevents_positive_write(self):
        self.bus.on_read = lambda: self.engine.submit(self.body("grid_off", id="command_0002"))
        result = self.execute(self.body())
        self.assertEqual(result["error"], "superseded_by_off")
        self.assertFalse(self.bus.writes)

    def test_expired_queued_command_never_writes(self):
        body = self.body()
        self.engine.submit(body)
        with patch("deye_control_core.time.time", return_value=body["expires_at"] + 1):
            self.engine.execute(body["id"])
        self.assertEqual(self.engine.get(body["id"])["state"], "expired")
        self.assertFalse(self.bus.writes)

    def test_session_expired_while_waiting_cannot_authorize_a_write(self):
        body = self.body()
        self.engine.submit(body)
        self.engine.session_until = 0
        self.engine.execute(body["id"])
        self.assertEqual(self.engine.get(body["id"])["error"], "manual_session_expired")
        self.assertFalse(self.bus.writes)

    def test_partial_reads_do_not_authorize_on(self):
        self.bus.partial_read = True
        result = self.execute(self.body())
        self.assertEqual(result["error"], "readback_unavailable")
        self.assertFalse(self.bus.writes)

    def test_unknown_grid_state_full_soc_or_invalid_voltage_prevents_on(self):
        for key, value in ((194, 2), (194, 0), (184, 100), (183, 100)):
            with self.subTest(key=key, value=value):
                self.bus.regs = sample_regs()
                self.bus.regs[key] = value
                result = self.execute(self.body(id="command_" + str(key) + "_" + str(value)))
                self.assertEqual(result["state"], "failed")
                self.assertFalse(self.bus.writes)

    def test_hardware_limit_below_operational_limit_is_enforced(self):
        self.bus.regs[210] = 5
        result = self.execute(self.body())
        self.assertEqual(result["error"], "battery_limit_exceeded")
        self.assertFalse(self.bus.writes)

    def test_preview_and_status_do_not_issue_any_io(self):
        self.bus.on_read = lambda: self.fail("read attempted by preview")
        self.engine.preview(self.body())
        self.engine.status()
        self.assertFalse(self.bus.writes)

    def test_disabled_installation_rejects_every_real_command(self):
        self.engine.writes_enabled = False
        for action in ("grid_on", "grid_off", "set_mode"):
            with self.subTest(action=action), self.assertRaisesRegex(ControlError, "writes_disabled"):
                self.engine.submit(
                    self.body(action, **({"work_mode": "SELLING_FIRST"} if action == "set_mode" else {}))
                )
        self.assertFalse(self.bus.writes)

    def test_stale_or_failed_frame_stays_unavailable_even_with_cached_values(self):
        self.engine.record_frame(self.bus.regs, time.time() - 100, time.time() - 99)
        self.assertFalse(self.engine.status()["available"])
        self.engine.record_frame({}, time.time(), time.time(), "acquisition_budget")
        self.assertFalse(self.engine.status()["available"])
        self.assertIsNotNone(self.engine.status()["sample"])

    def test_crash_recovery_marks_attempted_write_uncertain_without_replay(self):
        body = self.body()
        self.engine.submit(body)
        self.engine.journal.records[body["id"]].update(state="executing", write_attempted=True)
        self.engine.journal.save()
        self.engine.close()
        self.engine = Engine(self.bus, self.directory.name, writes_enabled=True, start_worker=False)
        self.assertEqual(self.engine.get(body["id"])["state"], "uncertain")
        self.assertFalse(self.bus.writes)

    def test_no_second_executor_can_own_same_journal(self):
        with self.assertRaises(BlockingIOError):
            Engine(self.bus, self.directory.name, start_worker=False)

    def test_atomic_intent_is_durable_before_device_write(self):
        original = self.bus.write_register_uint

        def inspect(key, value):
            durable = json.loads((Path(self.directory.name) / "commands.json").read_text())
            self.assertTrue(durable["commands"]["command_0001"]["write_attempted"])
            return original(key, value)

        self.bus.write_register_uint = inspect
        self.execute(self.body())


class ProtocolTests(unittest.TestCase):
    def test_crc_matches_independent_modbus_check_vector(self):
        from deye_control_transport import crc16

        self.assertEqual(crc16(b"123456789"), 0x4B37)

    def bus(self, response):
        bus = FakeModbus()

        class Connector:
            def send_request(self, request):
                return response

        bus.connector = Connector()
        return StrictModbus(bus)

    def test_strict_read_rejects_crossed_unit_function_bytecount_crc_and_truncation(self):
        valid = b"\x01\x03\x02\x00\x01"
        self.assertEqual(self.bus(frame(valid)).read_registers(194, 194), {194: b"\0\1"})
        for payload in (b"\x02" + valid[1:], b"\x01\x04" + valid[2:], b"\x01\x03\x04" + valid[3:], b"\x01\x83\x02"):
            self.assertEqual(self.bus(frame(payload)).read_registers(194, 194), {})
        for response in (frame(valid)[:-1], frame(valid) + b"\0", frame(valid)[:-1] + b"\0"):
            self.assertEqual(self.bus(response).read_registers(194, 194), {})

    def test_write_ack_requires_same_unit_function_address_count_and_crc(self):
        ack = b"\x01\x10\x00\xe6\x00\x01"
        self.assertTrue(self.bus(frame(ack)).write_register_uint(230, 10))
        for payload in (b"\x02" + ack[1:], b"\x01\x06" + ack[2:], ack[:3] + b"\xe7" + ack[4:], ack[:-1] + b"\x02"):
            self.assertFalse(self.bus(frame(payload)).write_register_uint(230, 10))
        with self.assertRaises(ValueError):
            self.bus(frame(ack)).write_register_uint(210, 100)

    def test_schema_rejects_nan_bool_ampere_and_unknown_fields(self):
        for fields in (
            {"ampere": True},
            {"ampere": 66},
            {"ampere": -1},
            {"expires_at": float("nan")},
            {"raw_register": 230},
        ):
            with self.assertRaises(ControlError):
                normalize({"action": "grid_on", "ampere": 10, "expected_revision": "0" * 64, **fields})
