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

"""Offline regression scenarios: fragmented TCP, bounded snapshots, recovery and TOU races."""

from datetime import datetime
import socket
import threading
from types import SimpleNamespace
from unittest.mock import Mock

from paho.mqtt.client import MQTTMessage
import pytest

import deye_daemon as daemon
import deye_io as io
import deye_tcp_connector as tcp
from deye_at_connector import DeyeAtConnector
from deye_config import DeyeConfig
from deye_events import DeyeEventList, DeyeObservationEvent
from deye_inverter_state import DeyeInverterState
from deye_modbus import DeyeModbus
from deye_modbus_tcp import DeyeModbusTcp
from deye_modbus_tcp_custom import DeyeModbusTcpCustom
from deye_observation import Observation
from deye_timeofuse_service import DeyeTimeOfUseService
from deye_sensors_deye_sg04lp3 import deye_sg04lp3_time_of_use_148 as sensor_one
from deye_sensors_deye_sg04lp3 import deye_sg04lp3_time_of_use_150 as sensor_two
from tests.deye_tcp_connector_test import Config, response
from tests.deye_inverter_state_test import FakeSensor


class Clock:
    def __init__(self):
        self.now = 0.0

    def __call__(self):
        return self.now


class Socket:
    def __init__(self, fragments, clock=None, delay=0):
        self.fragments = iter(fragments)
        self.clock, self.delay = clock, delay
        self.sent = []
        self.timeouts = []
        self.closed = 0
        self.receives = 0

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.closed += 1

    def settimeout(self, timeout):
        self.timeouts.append(timeout)

    def sendall(self, frame):
        self.sent.append(frame)

    def recv(self, size):
        self.receives += 1
        if self.clock is not None:
            self.clock.now += min(self.delay, self.timeouts[-1])
            if self.delay >= self.timeouts[-1]:
                raise socket.timeout("synthetic deadline")
        value = next(self.fragments, b"")
        if isinstance(value, Exception):
            raise value
        return value


def exchange(monkeypatch, sock, protocol="tcp"):
    cfg = Config()
    cfg.protocol = protocol
    monkeypatch.setattr(tcp.socket, "create_connection", lambda *a, **k: sock)
    return tcp.DeyeTcpConnector(cfg).send_request(b"synthetic-write-once")


@pytest.mark.parametrize("protocol", ["tcp", "mbtcp"])
@pytest.mark.parametrize("split", [1, 2, 3, 5, 6, 7, 8, 10])
def test_fragmented_response_is_assembled(monkeypatch, protocol, split):
    frame = response(bytes.fromhex("011000fa001e")) if protocol == "tcp" else bytes.fromhex("000100000006011000fa001e")
    sock = Socket([frame[:split], frame[split:]])
    assert exchange(monkeypatch, sock, protocol) == frame
    assert len(sock.sent) == 1
    assert sock.closed == 1


@pytest.mark.parametrize("fragments", [[b""], [socket.timeout()], [b"\xa5", b""], [b"\xa5", OSError()]])
def test_eof_or_error_stops_without_retries(monkeypatch, fragments):
    sock = Socket(fragments)
    assert exchange(monkeypatch, sock) is None
    assert sock.receives == len(fragments)
    assert len(sock.sent) == 1
    assert sock.closed == 1


@pytest.mark.parametrize(
    "protocol,frame",
    [
        ("tcp", b"\xa5\xff\xff"),
        ("mbtcp", b"\x00\x01\x00\x00\x00\x00"),
        ("mbtcp", b"\x00\x01\x00\x00\xff\xff"),
        ("tcp", response(bytes.fromhex("011000fa001e")) + b"extra"),
    ],
)
def test_invalid_lengths_fail_closed(monkeypatch, protocol, frame):
    sock = Socket([frame])
    assert exchange(monkeypatch, sock, protocol) is None
    assert sock.closed == 1


def test_slow_fragments_share_one_deadline(monkeypatch):
    clock = Clock()
    monkeypatch.setattr(tcp.time, "monotonic", clock)
    sock = Socket([b"\xa5", b"\x20", b"\x00"] * 10, clock, delay=4)
    assert exchange(monkeypatch, sock) is None
    assert clock.now == 10
    assert sock.receives == 3
    assert len(sock.sent) == 1
    assert sock.closed == 1


def test_remaining_budget_bounds_connect_send_and_receive(monkeypatch):
    clock = Clock()
    monkeypatch.setattr(io.time, "monotonic", clock)
    sock = Socket([b"\xa5"], clock, delay=2)
    cfg = Config()

    def connect(*args, timeout):
        assert timeout == 0.5
        clock.now += 0.1
        return sock

    monkeypatch.setattr(tcp.socket, "create_connection", connect)
    with io.io_budget(0.5):
        assert tcp.DeyeTcpConnector(cfg).send_request(b"write") is None
    assert clock.now == 0.5
    assert all(0 < t <= 0.4 for t in sock.timeouts)
    assert len(sock.sent) == 1


def test_nested_budget_restores_outer_deadline_and_is_thread_local(monkeypatch):
    clock = Clock()
    monkeypatch.setattr(io.time, "monotonic", clock)
    results = []
    with io.io_budget(3):
        with io.io_budget(20):
            assert io.io_timeout(30) == 3
        with io.io_budget(1):
            assert io.io_timeout(30) == 1
        worker = threading.Thread(target=lambda: results.append(io.io_timeout(30)))
        worker.start()
        worker.join(2)
        assert not worker.is_alive()
        assert io.io_timeout(30) == 3
    assert results == [30]
    assert io.io_timeout(30) == 30


def modbus_mock():
    return Mock(
        spec=DeyeModbus,
        transaction_lock=threading.RLock(),
        read_requested=threading.Event(),
        confirmation_read_requested=threading.Event(),
    )


def inverter(modbus, sensors=None, timeout=60, publish_on_change=False, processors=None):
    ranges = SimpleNamespace(ranges=[SimpleNamespace(first_reg_address=n, last_reg_address=n + 1) for n in [1, 3, 5]])
    config = SimpleNamespace(publish_on_change=publish_on_change, event_expiry=360)
    processor = Mock()
    state = DeyeInverterState(
        config,
        SimpleNamespace(index=0, logger_adapter=lambda log: log),
        ranges,
        modbus,
        sensors or [],
        processors or [processor],
        read_timeout=timeout,
    )
    return state, processor


def full_block(first, last):
    return {i: b"\x00\x2a" for i in range(first, last + 1)}


@pytest.mark.parametrize("failure", [{}, {3: b"\x00\x2a"}, OSError("synthetic")])
def test_failed_block_discards_entire_snapshot_and_stops(monkeypatch, failure):
    modbus = modbus_mock()
    modbus.read_registers.side_effect = [full_block(1, 2), failure, full_block(5, 6)]
    sensor = Mock(is_readiness_check=False)
    state, processor = inverter(modbus, [sensor], publish_on_change=True)
    assert state.read_from_logger() is False
    assert modbus.read_registers.call_count == 2
    sensor.read_value.assert_not_called()
    events = processor.process.call_args.args[0]
    assert len(events) == 1
    assert events.get_status() is True  # Reachability does not imply completeness.


def test_budget_discards_late_result_and_does_not_start_another_block(monkeypatch):
    clock = Clock()
    monkeypatch.setattr(io.time, "monotonic", clock)
    modbus = modbus_mock()

    def slow(first, last):
        clock.now += 0.4
        return full_block(first, last)

    modbus.read_registers.side_effect = slow
    state, processor = inverter(modbus, timeout=0.5)
    assert state.read_from_logger() is False
    assert modbus.read_registers.call_count == 2
    assert len(processor.process.call_args.args[0]) == 1


def test_budget_includes_waiting_for_transaction_lock():
    modbus = modbus_mock()
    modbus.transaction_lock = Mock()
    modbus.transaction_lock.acquire.return_value = False
    state, processor = inverter(modbus, timeout=0.01)
    assert state.read_from_logger() is False
    modbus.read_registers.assert_not_called()
    modbus.transaction_lock.release.assert_not_called()
    assert processor.process.call_args.args[0].read_started_at is None


def test_processors_run_after_releasing_transaction_lock():
    modbus = modbus_mock()
    modbus.read_registers.side_effect = full_block
    processor = Mock()
    acquired = []

    def process(events):
        def contender():
            with io.io_lock(modbus.transaction_lock, maximum=0.2):
                acquired.append(True)

        worker = threading.Thread(target=contender)
        worker.start()
        worker.join(1)
        assert not worker.is_alive()

    processor.process.side_effect = process
    state, _ = inverter(modbus, processors=[processor])
    assert state.read_from_logger() is True
    assert acquired == [True]


def test_absent_readiness_sensor_prevents_publication():
    modbus = modbus_mock()
    modbus.read_registers.side_effect = full_block
    sensor = FakeSensor("missing", None, is_readiness_check=True)
    state, processor = inverter(modbus, [sensor])
    assert state.read_from_logger() is False
    assert len(processor.process.call_args.args[0]) == 1


def test_confirmation_publishes_even_when_values_unchanged():
    modbus = modbus_mock()
    modbus.read_registers.side_effect = full_block
    state, processor = inverter(modbus, [FakeSensor("constant", 42)], publish_on_change=True)
    assert state.read_from_logger() is True
    assert state.read_from_logger() is True
    assert processor.process.call_count == 1
    modbus.confirmation_read_requested.set()
    assert state.read_from_logger() is True
    assert processor.process.call_count == 2
    assert not modbus.confirmation_read_requested.is_set()


class WakeEvent:
    def __init__(self, clock, hook=None):
        self.clock, self.hook, self.flag = clock, hook, False

    def set(self):
        self.flag = True

    def clear(self):
        self.flag = False

    def is_set(self):
        return self.flag

    def wait(self, timeout):
        if self.hook:
            hook, self.hook = self.hook, None
            hook(self, timeout)
        if not self.flag:
            self.clock.now += timeout
        return self.flag


def run_schedule(monkeypatch, results, duration=0, during=None, before_wait=None):
    clock = Clock()
    monkeypatch.setattr(daemon.time, "monotonic", clock)
    monkeypatch.setattr(daemon.random, "uniform", lambda *args: 0)
    wake = WakeEvent(clock)
    priority = threading.Event()
    times = []

    def action():
        priority.clear()
        index = len(times)
        times.append(clock.now)
        clock.now += duration
        if during:
            during(index, wake, priority)
        if index == len(results) - 1:
            runner.stop()
        elif before_wait:
            wake.hook = lambda event, timeout: before_wait(index, clock, event, priority)
        return results[index]

    runner = daemon.IntervalRunner(Config(), 60, action, wake, priority)
    runner._IntervalRunner__handler()
    return times


def test_runner_waits_from_completion_and_coalesces_generic_refreshes(monkeypatch):
    def refresh(index, wake, priority):
        for _ in range(100):
            wake.set()

    assert run_schedule(monkeypatch, [True, True], duration=70, during=refresh) == [0, 130]


def test_runner_backoff_and_success_reset(monkeypatch):
    assert run_schedule(monkeypatch, [False, False, False, False, True, True]) == [0, 5, 15, 35, 65, 125]


def test_generic_refresh_does_not_bypass_failure_cooldown(monkeypatch):
    def refresh(index, clock, wake, priority):
        wake.set()

    assert run_schedule(monkeypatch, [False, True], before_wait=refresh) == [0, 5]


def test_post_write_confirmation_bypasses_cooldown(monkeypatch):
    def confirm(index, clock, wake, priority):
        clock.now += 1
        priority.set()
        wake.set()

    assert run_schedule(monkeypatch, [False, True], before_wait=confirm) == [0, 1]


def test_confirmation_requested_during_poll_is_not_lost(monkeypatch):
    def confirm(index, wake, priority):
        if index == 0:
            priority.set()
            wake.set()

    assert run_schedule(monkeypatch, [True, True], duration=2, during=confirm) == [0, 2]


def service():
    modbus = modbus_mock()
    modbus.write_registers.return_value = True
    cfg = SimpleNamespace(index=0, logger_adapter=lambda log: log)
    svc = DeyeTimeOfUseService(cfg, Mock(), [sensor_one, sensor_two], modbus)
    return svc, modbus


def observed(started=None, sensors=(sensor_one, sensor_two)):
    events = DeyeEventList([DeyeObservationEvent(Observation(s, datetime.now(), 500)) for s in sensors])
    events.read_started_at = started
    return events


@pytest.mark.parametrize("failure", [False, True])
def test_write_readback_requested_after_completion_and_failed_batch_stops(failure):
    svc, modbus = service()
    svc.process(observed())
    modbus.write_registers.return_value = not failure
    requested = []

    def request(confirmation=False):
        assert confirmation
        assert not svc.read_state
        assert svc._DeyeTimeOfUseService__write_completed_at is not None
        assert modbus.transaction_lock.acquire(blocking=False)
        modbus.transaction_lock.release()
        requested.append(True)

    modbus.request_read.side_effect = request
    assert svc.write_config(False) is not failure
    assert modbus.write_registers.call_count == (1 if failure else 2)
    assert requested == [True]


def test_prewrite_publication_cannot_restore_stale_tou_state():
    svc, modbus = service()
    svc.process(observed())
    assert svc.write_config(False)
    completed = svc._DeyeTimeOfUseService__write_completed_at
    svc.process(observed(completed - 1))
    assert not svc.read_state
    assert svc.write_config(False) is False
    assert modbus.write_registers.call_count == 2
    svc.process(observed(completed + 1))
    assert len(svc.read_state) == 2


def test_partial_tou_state_refuses_write_and_only_requests_generic_read():
    svc, modbus = service()
    svc.process(observed(sensors=(sensor_one,)))
    assert svc.write_config(False) is False
    modbus.write_registers.assert_not_called()
    modbus.request_read.assert_called_once_with()


def message(payload, retained=False):
    msg = MQTTMessage(1, b"timeofuse/control/command")
    msg.payload, msg.retain = payload, retained
    return msg


def test_mqtt_callback_stays_responsive_and_only_keeps_latest_pending():
    svc, modbus = service()
    entered, release = threading.Event(), threading.Event()
    applied = []

    def apply(changes, dry):
        applied.append(changes)
        if len(applied) == 1:
            entered.set()
            assert release.wait(3)

    svc._DeyeTimeOfUseService__apply_config = apply
    svc.modifications[sensor_one] = "0600"
    svc.handle_control_command(None, None, message(b"write"))
    assert entered.wait(2)
    try:
        svc.modifications[sensor_one] = "0700"
        svc.handle_control_command(None, None, message(b"write"))
        svc.modifications[sensor_one] = "0800"
        svc.handle_control_command(None, None, message(b"write"))
        worker = svc._DeyeTimeOfUseService__worker
    finally:
        release.set()
    worker.join(3)
    assert not worker.is_alive()
    assert applied == [{sensor_one: "0600"}, {sensor_one: "0800"}]


@pytest.mark.parametrize("payload", [b"write", b"dry-write", b"reset"])
def test_retained_control_messages_are_ignored(payload):
    svc, modbus = service()
    svc.modifications[sensor_one] = "0600"
    svc.handle_control_command(None, None, message(payload, retained=True))
    assert svc.modifications == {sensor_one: "0600"}
    assert svc._DeyeTimeOfUseService__worker is None
    modbus.write_registers.assert_not_called()


@pytest.mark.parametrize("seconds", [0, -1])
def test_nonpositive_acquisition_budget_is_rejected(seconds):
    with pytest.raises(ValueError, match="must be positive"):
        DeyeConfig(logger_configs=[], mqtt=None, data_read_timeout=seconds)


@pytest.mark.parametrize("protocol", ["tcp", "mbtcp"])
@pytest.mark.parametrize("write", [False, True])
def test_fragmentation_through_actual_protocol_adapter_and_modbus(monkeypatch, protocol, write):
    cfg = Config()
    cfg.protocol = protocol
    request = bytes.fromhex("011000fa0002") if write else bytes.fromhex("010300010002")
    if protocol == "tcp":
        frame = response(request)
        adapter = DeyeModbusTcpCustom
    else:
        payload = request if write else bytes.fromhex("010304002a002a")
        frame = b"\x00\x01\x00\x00" + len(payload).to_bytes(2, "big") + payload
        adapter = DeyeModbusTcp
    sock = Socket([frame[i : i + 1] for i in range(len(frame))])
    monkeypatch.setattr(tcp.socket, "create_connection", lambda *a, **k: sock)
    modbus = DeyeModbus(adapter(cfg, tcp.DeyeTcpConnector(cfg)))
    if write:
        assert modbus.write_registers_uint(250, [42, 42]) is True
    else:
        assert modbus.read_registers(1, 2) == {1: b"\x00\x2a", 2: b"\x00\x2a"}
    assert len(sock.sent) == 1
    assert sock.closed == 1


def test_reset_cancels_pending_request_without_replaying_executing_request():
    svc, _ = service()
    entered, release = threading.Event(), threading.Event()
    applied = []

    def apply(changes, dry):
        applied.append(changes)
        entered.set()
        assert release.wait(3)

    svc._DeyeTimeOfUseService__apply_config = apply
    svc.modifications[sensor_one] = "0600"
    svc.handle_control_command(None, None, message(b"write"))
    assert entered.wait(2)
    try:
        svc.modifications[sensor_one] = "0700"
        svc.handle_control_command(None, None, message(b"write"))
        svc.handle_control_command(None, None, message(b"reset"))
        worker = svc._DeyeTimeOfUseService__worker
    finally:
        release.set()
    worker.join(3)
    assert not worker.is_alive()
    assert applied == [{sensor_one: "0600"}]


def test_retained_staged_modifications_are_ignored():
    svc, modbus = service()
    svc.initialize()
    svc.handle_command(None, None, message(b"0600", retained=True))
    assert not svc.modifications
    modbus.write_registers.assert_not_called()


def test_entire_acquisition_cannot_interleave_with_multi_batch_tou_write():
    svc, modbus = service()
    svc.process(observed())
    entered, release, contended = threading.Event(), threading.Event(), threading.Event()
    calls = []

    class TransactionLock:
        def __init__(self):
            self.lock = threading.RLock()

        def acquire(self, timeout):
            if self.lock.acquire(blocking=False):
                return True
            contended.set()
            return self.lock.acquire(timeout=timeout)

        def release(self):
            self.lock.release()

    modbus.transaction_lock = TransactionLock()

    def read(first, last):
        calls.append(("read", first))
        if first == 1:
            entered.set()
            assert release.wait(3)
        return full_block(first, last)

    def write(first, values):
        calls.append(("write", first))
        return True

    modbus.read_registers.side_effect = read
    modbus.write_registers.side_effect = write
    state, _ = inverter(modbus)
    reader = threading.Thread(target=state.read_from_logger)
    writer = threading.Thread(target=lambda: svc.write_config(False))
    reader.start()
    try:
        assert entered.wait(2)
        writer.start()
        assert contended.wait(2)
        assert calls == [("read", 1)]
    finally:
        release.set()
        reader.join(3)
        if writer.ident is not None:
            writer.join(3)
    assert not reader.is_alive() and not writer.is_alive()
    assert calls == [("read", 1), ("read", 3), ("read", 5), ("write", 148), ("write", 150)]


def test_first_recovery_republishes_unchanged_values_after_failed_confirmation():
    modbus = modbus_mock()
    modbus.read_registers.side_effect = full_block
    state, processor = inverter(modbus, [FakeSensor("constant", 42)], publish_on_change=True)
    assert state.read_from_logger() is True
    modbus.confirmation_read_requested.set()
    modbus.read_registers.side_effect = lambda *args: {}
    assert state.read_from_logger() is False
    assert not modbus.confirmation_read_requested.is_set()
    modbus.read_registers.side_effect = full_block
    assert state.read_from_logger() is True
    assert processor.process.call_count == 3
    assert len(processor.process.call_args.args[0]) == 2
    assert state.read_from_logger() is True
    assert processor.process.call_count == 3


def test_expired_at_budget_does_not_create_or_leak_a_socket(monkeypatch):
    clock = Clock()
    monkeypatch.setattr(io.time, "monotonic", clock)
    factory = Mock()
    monkeypatch.setattr(socket, "socket", factory)
    with io.io_budget(1):
        clock.now = 2
        assert DeyeAtConnector(Config()).send_request(b"write") is None
    factory.assert_not_called()
