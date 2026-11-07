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


import logging
from types import SimpleNamespace

import pytest

import deye_at_connector
from deye_at_connector import DeyeAtConnector
from deye_config import DeyeLoggerConfig
from deye_modbus import DeyeModbus


@pytest.fixture(scope="module")
def connector():
    return DeyeAtConnector(DeyeLoggerConfig(123456, "192.168.0.1", 9090))


class TestDeyeAtConnector:
    def test_extract_modbus_frame_with_trailing_zeros(self, connector):
        # given
        at_cmd_response = (
            b"+ok=01\x1003\x1072\x1001\x1008\x1000\x1000\x1002\x1094\x106C\x106B\x1000"
            b"\x1000\x1000\x1000\x1000\x1000\x1000\x1000\x1000\x1000\x1000\x1000\x1010\x1029\x100F"
            b"\x1067\x1010\x1005\x1009\x1055\x1008\x10E5\x1009\x1040\x1000\x100F\x1000\x100E\x1000"
            b"\x100F\x1013\x1084\x1024\x10DB\x1000\x1000\x1022\x10AA\x1000\x1000\x1002\x10B2\x1000"
            b"\x1000\x1025\x10C2\x1000\x1000\x1002\x10B2\x1000\x1000\x1005\x107B\x1005\x107B\x1000"
            b"\x1004\x1003\x10E8\x1000\x1000\x1000\x1000\x1000\x1000\x1000\x1000\x1000\x1010\x1000"
            b"\x1000\x1000\x1000\x1000\x1000\x1000\x1000\x1000\x1000\x1000\x1000\x1000\x1000\x1000"
            b"\x1000\x1000\x1000\x1000\x1000\x100E\x10FB\x1000\x1016\x1000\x1015\x1000\x1001\x1000"
            b"\x1000\x1000\x1000\x1000\x1000\x1000\x1000\x1057\x1045\x1000\x1000\x10\r\n\r\n"
        )

        # when
        modbus_response = connector.extract_modbus_response(at_cmd_response)

        # then
        assert modbus_response == bytearray.fromhex(
            "0103720108000002946C6B00000000000000000000000010290F671005095508E50940000F000E000F13842"
            "4DB000022AA000002B2000025C2000002B20000057B057B000403E800000000000000000010000000000000"
            "00000000000000000000000000000EFB00160015000100000000000000005745"
        )

    @pytest.mark.parametrize(
        "at_cmd_response,expected_log",
        [
            pytest.param(
                b"+ok=\xff\x10ab\r\n\r\n",
                f"AT response contains non-ASCII data: {b'+ok=\xff\x10ab\r\n\r\n'.hex()}",
                id="non_ascii_bytes",
            ),
            pytest.param(
                b"+ok=abc\r\n\r\n",
                "AT response has odd-length hex string: abc",
                id="odd_length_hex",
            ),
            pytest.param(
                b"+ok=zzzz\r\n\r\n",
                "AT response contains invalid hex data: zzzz",
                id="invalid_hex_chars",
            ),
        ],
    )
    def test_extract_modbus_response_returns_none(self, connector, at_cmd_response, expected_log, caplog):
        with caplog.at_level(logging.ERROR):
            result = connector.extract_modbus_response(at_cmd_response)
        assert result is None
        assert caplog.records[0].getMessage() == expected_log

    def test_extract_modbus_frame_without_trailing_zeros(self, connector):
        # given
        at_cmd_response = (
            b"+ok=01\x1003\x1072\x1000\x101D\x1000\x1000\x1000\x1000\x100F\x10F2\x1000"
            b"\x1000\x1000\x100E\x1000\x100E\x1000\x1000\x1000\x1000\x1007\x10BD\x1000"
            b"\x1000\x1007\x10D1\x1000\x1000\x1009\x1038\x1000\x1000\x1000\x1000\x1000"
            b"\x1001\x1000\x1000\x1000\x1000\x1013\x1088\x1000\x1000\x1000\x1000\x1000"
            b"\x1000\x1000\x1000\x1000\x1000\x1000\x1000\x1001\x1068\x1000\x1000\x1000"
            b"\x1000\x1000\x1000\x1012\x10E8\x1000\x1000\x1000\x1000\x1000\x1000\x1000"
            b"\x1000\x1000\x1000\x1000\x1000\x1000\x1000\x1000\x1000\x1000\x1000\x1000"
            b"\x1000\x1000\x1000\x1000\x1000\x1000\x1000\x1000\x1000\x1000\x1000\x1000"
            b"\x1000\x1000\x1000\x1000\x1000\x1000\x10EA\x1000\x1007\x1000\x10FA\x1000"
            b"\x1007\x1000\x1000\x1000\x1000\x1000\x1000\x1000\x1000\x1058\x10AB\x10\r\n\r\n"
        )

        # when
        modbus_response = connector.extract_modbus_response(at_cmd_response)

        # then
        assert modbus_response == bytearray.fromhex(
            "010372001D000000000FF20000000E000E0000000007BD000007D100000938000000000001"
            "000000001388000000000000000000000000016800000000000012E8000000000000000000"
            "00000000000000000000000000000000000000000000000000000000EA000700FA0007000000000000000058AB"
        )


class FakeUdpSocket:
    def __init__(self, modbus_response: str):
        self.sent = []
        self.replies = [
            b"192.168.1.50,ACCF23000000,HF-A11ASSISTHREAD",
            b"+ok=" + modbus_response.upper().encode("ascii") + b"\r\n\r\n",
        ]

    def settimeout(self, timeout):
        pass

    def sendto(self, data, address):
        self.sent.append(data)

    def recv(self, size):
        return self.replies.pop(0)

    def close(self):
        pass


class TestDeyeAtConnectorModbusId:
    @pytest.fixture
    def udp_socket(self, monkeypatch):
        monkeypatch.setattr(deye_at_connector, "time", SimpleNamespace(sleep=lambda seconds: None))

        def install(modbus_response):
            sock = FakeUdpSocket(modbus_response)
            monkeypatch.setattr(deye_at_connector.socket, "socket", lambda family, kind: sock)
            return sock

        return install

    @pytest.mark.parametrize(
        "modbus_id,request_frame,response_frame",
        [
            (0x00, "000300020002641a", "000304000a000b8b36"),
            (0x01, "01030002000265cb", "010304000a000b9bf6"),
            (0xF7, "f70300020002715d", "f70304000a000b0df9"),
        ],
    )
    def test_read_registers_with_modbus_id(self, udp_socket, modbus_id, request_frame, response_frame):
        # given
        sock = udp_socket(response_frame)
        sut = DeyeModbus(DeyeAtConnector(DeyeLoggerConfig(1234567890, "192.168.1.50", 0, protocol="at")), modbus_id)

        # when
        reg_values = sut.read_registers(2, 3)

        # then
        assert f"AT+INVDATA=8,{request_frame}\n".encode("ascii") in sock.sent
        assert reg_values == {2: bytearray.fromhex("000a"), 3: bytearray.fromhex("000b")}

    @pytest.mark.parametrize(
        "modbus_id,request_frame,response_frame",
        [
            (0x00, "00100012000102a3d4d01d", "001000120001a01d"),
            (0x01, "01100012000102a3d4dd8d", "011000120001a1cc"),
            (0xF7, "f7100012000102a3d4f229", "f71000120001b55a"),
        ],
    )
    def test_write_register_with_modbus_id(self, udp_socket, modbus_id, request_frame, response_frame):
        # given
        sock = udp_socket(response_frame)
        sut = DeyeModbus(DeyeAtConnector(DeyeLoggerConfig(1234567890, "192.168.1.50", 0, protocol="at")), modbus_id)

        # when
        success = sut.write_register_uint(0x12, 0xA3D4)

        # then
        assert f"AT+INVDATA=11,{request_frame}\n".encode("ascii") in sock.sent
        assert success is True
