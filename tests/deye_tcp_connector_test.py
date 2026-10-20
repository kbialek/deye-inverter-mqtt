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

from concurrent.futures import ThreadPoolExecutor
from queue import Queue
import socket
import threading
from unittest.mock import patch

import pytest

import deye_tcp_connector as tcp
from deye_modbus import DeyeModbus
from deye_modbus_crc import modbus_crc
from deye_modbus_tcp_custom import DeyeModbusTcpCustom


class Config:
    # Synthetic identity used only to encode fixtures, never a real logger.
    ip_address = "inverter-a.invalid"
    port = 8899
    serial_number = 0x10203040

    @staticmethod
    def logger_adapter(logger):
        return logger


def response(request, wrong_read=False):
    if request[1] == 3 or wrong_read:
        count = 110 if wrong_read else int.from_bytes(request[4:6], "big")
        body = bytes([1, 3, count * 2]) + b"\x00\x2a" * count
    else:
        body = request[:6]
    modbus = body + modbus_crc(body).to_bytes(2, "little")
    packet = bytearray(25) + modbus + b"\x00\x15"
    packet[0] = 0xA5
    packet[1:3] = (len(packet) - 13).to_bytes(2, "little")
    packet[-2] = sum(packet[1:-2]) & 255
    return bytes(packet)


class Peer:
    def __init__(self, *, hold=False, cross=False, hold_close=False, failure=None):
        self.guard = threading.Lock()
        self.hold = hold
        self.cross = cross
        self.hold_close = hold_close
        self.failure = failure
        self.entered = threading.Event()
        self.release = threading.Event()
        self.second_open = threading.Event()
        self.close_entered = threading.Event()
        self.close_release = threading.Event()
        self.active = {}
        self.maximum = 0
        self.attempts = 0
        self.sockets = []
        self.requests = []
        self.crossed = False

    def connect(self, address, timeout):
        assert address[1] == 8899 and timeout == 10
        with self.guard:
            self.attempts += 1
            attempt = self.attempts
            if attempt == 1 and self.failure == "connect_error":
                raise OSError("synthetic connection failure")
            sock = FakeSocket(self, attempt)
            self.active[attempt] = sock
            self.sockets.append(sock)
            self.maximum = max(self.maximum, len(self.active))
            if attempt > 1:
                self.second_open.set()
            return sock


class FakeSocket:
    def __init__(self, peer, number):
        self.peer, self.number = peer, number
        self.request = None
        self.reply = None
        self.recv_calls = 0
        self.close_calls = 0

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

    def sendall(self, packet):
        if self.number == 1 and self.peer.failure == "send_error":
            raise OSError("synthetic send failure")
        self.request = packet[26:-2]
        assert modbus_crc(self.request[:-2]) == int.from_bytes(self.request[-2:], "little")
        self.reply = response(self.request, self.number == 1 and self.peer.failure == "wrong_reply")
        with self.peer.guard:
            self.peer.requests.append(self.request)
            others = [s for s in self.peer.active.values() if s is not self and s.request is not None]
            if self.peer.cross and others:
                # Model the observed logger: a read reply reaches the outstanding
                # write, while the other socket exhausts its receive attempts.
                others[0].reply = self.reply
                self.reply = None
                self.peer.crossed = True

    def recv(self, size):
        assert size == 1024
        self.recv_calls += 1
        if self.number == 1 and self.peer.hold:
            self.peer.entered.set()
            assert self.peer.release.wait(3), "Test did not release its synthetic exchange"
        failure = self.peer.failure if self.number == 1 else None
        if failure == "timeout" or self.reply is None:
            raise socket.timeout("synthetic receive timeout")
        if failure == "empty":
            return b""
        if failure == "recv_error":
            raise OSError("synthetic receive failure")
        if failure == "recv_unexpected":
            raise RuntimeError("synthetic unexpected receive failure")
        return self.reply

    def close(self):
        self.close_calls += 1
        if self.number == 1 and self.peer.hold_close:
            self.peer.close_entered.set()
            assert self.peer.close_release.wait(3), "Test did not release synthetic socket close"
        with self.peer.guard:
            self.peer.active.pop(self.number, None)


def client(config=None):
    cfg = config or Config()
    connector = tcp.DeyeTcpConnector(cfg)
    return DeyeModbus(DeyeModbusTcpCustom(cfg, connector))


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    def deny(*args, **kwargs):
        pytest.fail("TCP connector tests must not access a real device")

    monkeypatch.setattr(socket, "create_connection", deny)
    monkeypatch.setattr(socket.socket, "connect", deny)
    monkeypatch.setattr(socket.socket, "connect_ex", deny)


@pytest.mark.parametrize("first_write", [False, True], ids=["read-then-write", "write-then-read"])
def test_read_write_exchanges_do_not_overlap(first_write):
    peer = Peer(hold=True, cross=True)
    bridge = client()

    def read():
        return bridge.read_registers(3, 112)

    def write():
        return bridge.write_registers_uint(250, [50] * 30)

    first, second = (write, read) if first_write else (read, write)
    began = threading.Event()

    def contender():
        began.set()
        return second()

    with patch.object(tcp.socket, "create_connection", peer.connect), ThreadPoolExecutor(2) as pool:
        one = pool.submit(first)
        try:
            assert peer.entered.wait(2)
            two = pool.submit(contender)
            assert began.wait(2)
            peer.second_open.wait(0.1)
        finally:
            peer.release.set()
        results = [one.result(timeout=3), two.result(timeout=3)]

    assert peer.maximum == 1, "Local read/write exchanges overlapped"
    assert not peer.crossed
    assert results[0 if first_write else 1] is True
    values = results[1 if first_write else 0]
    assert len(values) == 110
    assert all(int.from_bytes(v, "big") == 42 for v in values.values())
    assert all(s.close_calls == 1 for s in peer.sockets)


def test_independent_inverters_can_exchange_concurrently():
    a, b = Peer(hold=True), Peer()
    cfg_b = Config()
    cfg_b.ip_address = "inverter-b.invalid"
    one, two = client(), client(cfg_b)

    def connect(address, timeout):
        return (a if address[0] == Config.ip_address else b).connect(address, timeout)

    with patch.object(tcp.socket, "create_connection", connect), ThreadPoolExecutor(2) as pool:
        first = pool.submit(one.read_registers, 3, 4)
        try:
            assert a.entered.wait(2)
            second = pool.submit(two.read_registers, 3, 4)
            assert len(second.result(timeout=2)) == 2
        finally:
            a.release.set()
        assert len(first.result(timeout=3)) == 2


def test_socket_closes_before_the_next_exchange():
    peer = Peer(hold_close=True)
    bridge = client()
    began = threading.Event()

    def write():
        began.set()
        return bridge.write_register_uint(250, 50)

    with patch.object(tcp.socket, "create_connection", peer.connect), ThreadPoolExecutor(2) as pool:
        first = pool.submit(bridge.read_registers, 3, 4)
        try:
            assert peer.close_entered.wait(2)
            second = pool.submit(write)
            assert began.wait(2)
            assert not peer.second_open.wait(0.1), "The next exchange started before socket close finished"
        finally:
            peer.close_release.set()
        assert len(first.result(timeout=3)) == 2
        assert second.result(timeout=3) is True
    assert peer.maximum == 1
    assert all(s.close_calls == 1 for s in peer.sockets)


@pytest.mark.parametrize(
    "failure",
    ["connect_error", "send_error", "timeout", "empty", "recv_error", "recv_unexpected", "wrong_reply"],
)
def test_failed_exchange_releases_resources_and_allows_the_next_request(failure):
    peer = Peer(failure=failure)
    bridge = client()
    with patch.object(tcp.socket, "create_connection", peer.connect):
        if failure == "send_error":
            with pytest.raises(OSError, match="synthetic send failure"):
                bridge.write_register_uint(250, 50)
        else:
            assert bridge.write_register_uint(250, 50) is False

        # Bound the follow-up call even if a future regression leaks the lock.
        results = Queue()

        def follow_up():
            try:
                results.put(bridge.read_registers(3, 4))
            except Exception as exc:
                results.put(exc)

        worker = threading.Thread(target=follow_up, daemon=True)
        worker.start()
        worker.join(timeout=3)
        assert not worker.is_alive(), "Failed exchange left the connector locked"
        values = results.get_nowait()
        assert isinstance(values, dict)
        assert len(values) == 2

    assert peer.attempts == 2
    assert all(s.close_calls == 1 for s in peer.sockets)
    assert not peer.active
    if failure in ("timeout", "empty"):
        assert peer.sockets[0].recv_calls == 5
    # Receiving an error must not cause a write to be silently submitted again.
    writes = [r for r in peer.requests if r[1] == 16]
    assert len(writes) == (0 if failure in ("connect_error", "send_error") else 1)
