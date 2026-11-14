import json
import threading
import time
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from deye_control_core import ControlError, Engine, configuration_revision
from tests.deye_control_core_test import FakeModbus, sample_regs
from deye_control_processor import ControlProcessor, create_control
from deye_control_transport import StrictModbus, frame
from deye_inverter_state import DeyeInverterState
from deye_modbus import DeyeModbus
from deye_mqtt import DeyeMqttClient
from deye_timeofuse_service import DeyeTimeOfUseService


@pytest.fixture
def control(tmp_path):
    bus = FakeModbus()
    engine = Engine(bus, tmp_path, writes_enabled=True, start_worker=False)
    engine.record_frame(bus.regs, time.time() - 1, time.time())
    processor = ControlProcessor(engine, MagicMock(), 0)
    yield processor
    processor.close()


def message(request, retain=False):
    return SimpleNamespace(payload=json.dumps(request).encode(), retain=retain)


def request(operation="status", **fields):
    return {"schema": 1, "request_id": "request_0001", "op": operation, "body": {}, **fields}


def test_callback_rejects_retained_invalid_and_oversize_messages(control):
    for msg in (
        message(request(), True),
        message([]),
        message(request(request_id="short")),
        message(request(schema=2)),
        SimpleNamespace(retain=False, payload=b"{"),
        SimpleNamespace(retain=False, payload=b" " * 16385),
    ):
        control.handle_message(None, None, msg)
    assert control.requests.empty()
    assert not control.engine.modbus.writes


@pytest.mark.parametrize("body", [{"action": "grid_off"}, {"action": "set_current", "ampere": 0}])
def test_off_has_reserved_capacity_and_priority(control, body):
    for _ in range(60):
        control.handle_message(None, None, message(request()))
    assert control.requests.qsize() == 56
    control.handle_message(None, None, message(request("submit", body=body)))
    priority, _, received = control.requests.get_nowait()
    assert priority == 0 and received["body"] == body


@pytest.mark.parametrize("body", [{"action": "grid_off"}, {"action": "grid_off", "id": "command_0001"}])
def test_mqtt_submit_requires_publisher_id_and_deadline(control, body):
    with pytest.raises(ControlError, match="id_and_expiry_required"):
        control.dispatch(request("submit", body=body))
    assert not control.engine.journal.records


def test_manual_session_is_not_renewed_by_redelivery_or_restart(control, monkeypatch, tmp_path):
    session = request("session", body={"exclusive_window_confirmed": True}, expires_at=time.time() + 30)
    first = control.dispatch(session)
    control.engine.session_until = 0
    assert control.dispatch(session) == first
    assert control.engine.session_until == 0
    control.close()
    restarted = Engine(FakeModbus(), tmp_path, writes_enabled=True, start_worker=False)
    try:
        processor = ControlProcessor(restarted, MagicMock(), 0)
        assert processor.dispatch(session) == first
        assert restarted.session_until == 0
    finally:
        restarted.close()


def test_session_replay_with_changed_body_conflicts(control):
    session = request("session", body={"exclusive_window_confirmed": True}, expires_at=time.time() + 30)
    control.dispatch(session)
    with pytest.raises(ControlError, match="id_conflict"):
        control.dispatch({**session, "expires_at": session["expires_at"] + 1})


def test_status_preview_remain_read_only_without_manual_authority(control):
    body = {"action": "grid_on", "ampere": 5, "expected_revision": configuration_revision(sample_regs())}
    assert control.dispatch(request())["available"]
    assert control.dispatch(request("preview", body=body))["writes_performed"] is False
    with pytest.raises(ControlError, match="manual_session_required"):
        control.dispatch(request("submit", body={**body, "id": "command_0001", "expires_at": time.time() + 30}))
    assert not control.engine.modbus.writes


def test_service_authority_and_lower_installation_current_cap_are_explicit(tmp_path):
    bus = FakeModbus()
    engine = Engine(bus, tmp_path, writes_enabled=True, authority="service", max_ampere=5, start_worker=False)
    try:
        with pytest.raises(ControlError, match="manual_sessions_disabled"):
            engine.open_session({"exclusive_window_confirmed": True})
        body = {"action": "grid_on", "ampere": 6, "expected_revision": configuration_revision(bus.regs)}
        with pytest.raises(ControlError, match="ampere_out_of_range"):
            engine.submit(body)
        accepted = engine.submit({**body, "ampere": 5})
        engine.execute(accepted["id"])
        assert engine.get(accepted["id"])["state"] == "confirmed"
    finally:
        engine.close()


@pytest.mark.parametrize("started,completed", [(1, 2), (-1, 1), (-2, -3)])
def test_future_or_reversed_timestamps_cannot_authorize_availability(control, started, completed):
    now = time.time()
    control.engine.record_frame(sample_regs(), now + started, now + completed)
    assert control.engine.status()["available"] is False


def test_feature_disabled_does_not_construct_a_device_or_journal(monkeypatch, tmp_path):
    monkeypatch.delenv("DEYE_FEATURE_LOCAL_CONTROL", raising=False)
    assert create_control(None, None, None, None) is None
    assert not list(tmp_path.iterdir())


@pytest.mark.parametrize("conflict", ["DEYE_FEATURE_BATTERY_SETTINGS", "DEYE_FEATURE_WORKMODE"])
def test_legacy_scalar_writers_cannot_bypass_transactional_policy(monkeypatch, conflict):
    monkeypatch.setenv("DEYE_FEATURE_LOCAL_CONTROL", "true")
    monkeypatch.setenv(conflict, "true")
    with pytest.raises(ValueError, match="conflicts"):
        create_control(None, None, None, None)


def test_model_and_persistent_storage_are_required_and_writes_default_off(monkeypatch, tmp_path):
    monkeypatch.setenv("DEYE_FEATURE_LOCAL_CONTROL", "true")
    config = SimpleNamespace(metric_groups=["deye_hybrid", "deye_hybrid_battery", "deye_hybrid_timeofuse"])
    logger = SimpleNamespace(index=0)
    with pytest.raises(ValueError, match="explicit supported model"):
        create_control(config, logger, None, None)
    monkeypatch.setenv("DEYE_CONTROL_MODEL", "sg03lp1")
    with pytest.raises(ValueError, match="persistent absolute"):
        create_control(config, logger, None, None)
    monkeypatch.setenv("DEYE_CONTROL_STATE_DIR", str(tmp_path))
    bus = FakeModbus()
    bus.connector = MagicMock()
    processor = create_control(config, logger, MagicMock(), bus)
    try:
        assert processor.engine.writes_enabled is False
        assert processor.engine.authority == "manual"
    finally:
        processor.close()


def test_configured_modbus_unit_is_preserved_without_a_second_connector():
    bus = FakeModbus()
    bus.modbus_id = 2
    bus.connector = MagicMock()
    bus.connector.send_request.return_value = frame(b"\x02\x03\x02\x00\x01")
    strict = StrictModbus(bus)
    assert strict.read_registers(194, 194) == {194: b"\x00\x01"}
    assert bus.connector.send_request.call_args.args[0][0] == 2
    assert strict.transaction_lock is bus.transaction_lock
    bus.connector.send_request.return_value = frame(b"\x01\x03\x02\x00\x01")
    assert strict.read_registers(194, 194) == {}
    bus.connector.send_request.return_value = frame(b"\x02\x10\x00\xe6\x00\x01")
    assert strict.write_register_uint(230, 5)
    assert bus.connector.send_request.call_args.args[0][0] == 2


def test_raw_observer_runs_before_releasing_bus_but_publishers_run_after():
    bus = FakeModbus()
    bus.local_control = MagicMock()
    bus.local_control.off_pending.return_value = False
    owned = []
    bus.local_control.record_frame.side_effect = lambda *args: owned.append(bus.transaction_lock._is_owned())
    publisher = MagicMock()
    publisher.process.side_effect = lambda *args: owned.append(bus.transaction_lock._is_owned())
    logger = MagicMock(index=0)
    config = SimpleNamespace(publish_on_change=False)
    ranges = SimpleNamespace(
        ranges=[
            SimpleNamespace(first_reg_address=150, last_reg_address=213),
            SimpleNamespace(first_reg_address=214, last_reg_address=279),
        ]
    )
    state = DeyeInverterState(config, logger, ranges, bus, [], [publisher])
    state.read_from_logger()
    assert owned == [True, False]
    assert bus.local_control.record_frame.call_args.args[-1] is None
    bus.local_control.off_pending.return_value = True
    original_read = bus.read_registers
    bus.read_registers = MagicMock(wraps=original_read)
    state.read_from_logger()
    bus.read_registers.assert_not_called()
    assert bus.local_control.record_frame.call_args.args[-1] == "incomplete_acquisition"
    bus.local_control.off_pending.return_value = False
    bus.read_registers = MagicMock(side_effect=OSError("synthetic failure"))
    with pytest.raises(OSError):
        state.read_from_logger()
    assert bus.local_control.record_frame.call_args.args[-1] == "incomplete_acquisition"
    assert not bus.transaction_lock._is_owned()


def test_native_modbus_waits_for_the_same_transaction_lock():
    connector = MagicMock()
    connector.send_request.return_value = frame(b"\x01\x03\x02\x00\x01")
    bus = DeyeModbus(connector)
    entered = threading.Event()

    def read():
        entered.set()
        bus.read_registers(194, 194)

    with bus.transaction_lock:
        thread = threading.Thread(target=read)
        thread.start()
        assert entered.wait(1)
        assert not connector.send_request.called
    thread.join(1)
    assert not thread.is_alive()
    assert connector.send_request.called


def test_all_tou_batches_hold_the_transaction_lock():
    bus = FakeModbus()
    held = []
    bus.write_registers = lambda *args: held.append(bus.transaction_lock._is_owned()) or True
    sensor = MagicMock()
    sensor.mqtt_topic_suffix = "timeofuse/test"
    sensor.write_value.return_value = {250: b"\x00\x01", 252: b"\x00\x02"}
    service = DeyeTimeOfUseService(MagicMock(), MagicMock(), [sensor], bus)
    service._DeyeTimeOfUseService__read_state = {sensor: "test"}
    service.write_config(False)
    assert held == [True, True]


def test_result_publication_never_waits_or_uses_global_retain(monkeypatch):
    client = MagicMock()
    client.publish.return_value.rc = 0
    monkeypatch.setattr("deye_mqtt.paho.Client", lambda **kwargs: client)
    config = MagicMock()
    config.mqtt.topic_prefix = "test"
    config.mqtt.tls.enabled = False
    mqtt = DeyeMqttClient(config)
    assert mqtt.publish_control(2, "control/result", "{}")
    client.publish.assert_called_once_with("test/2/control/result", "{}", qos=1, retain=False)
    client.publish.return_value.wait_for_publish.assert_not_called()
    client.is_connected.return_value = False
    assert mqtt.publish_control(0, "control/state", "{}") is False
    assert client.publish.call_count == 1
