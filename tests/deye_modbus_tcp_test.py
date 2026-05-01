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

import libscrc
import unittest
from unittest.mock import patch

from deye_config import DeyeConfig, DeyeLoggerConfig
from deye_modbus import DeyeModbus
from deye_modbus_tcp import DeyeModbusTcp


class DeyeModbusTcpTest(unittest.TestCase):
    def _compute_crc_bytes(self, frame: bytearray) -> bytearray:
        """Compute and return the CRC bytes in little-endian format (matching Modbus TCP wire format)."""
        crc = bytearray.fromhex("{:04x}".format(libscrc.modbus(frame)))
        crc.reverse()
        return crc

    def setUp(self):
        self.config = DeyeLoggerConfig(1234567890, "192.168.1.1", 8899)

    @patch("deye_connector.DeyeConnector")
    def test_read_register_0x01(self, connector):
        # given
        sut = DeyeModbus(DeyeModbusTcp(self.config, connector))
        connector.send_request.return_value = bytearray.fromhex("00010000000501" + "0302000a")

        # when
        reg_values = sut.read_registers(1, 1)

        # then
        self.assertEqual(len(reg_values), 1)
        self.assertTrue(1 in reg_values)
        self.assertEqual(reg_values[1].hex(), "000a")

    @patch("deye_connector.DeyeConnector")
    def test_read_registers_0x02_0x03(self, connector):
        # given
        sut = DeyeModbus(DeyeModbusTcp(self.config, connector))
        connector.send_request.return_value = bytearray.fromhex("00010000000701" + "0302000a000b")

        # when
        reg_values = sut.read_registers(2, 3)

        # then
        self.assertEqual(len(reg_values), 2)
        self.assertTrue(2 in reg_values)
        self.assertTrue(3 in reg_values)
        self.assertEqual(reg_values[2].hex(), "000a")
        self.assertEqual(reg_values[3].hex(), "000b")

        # and
        connector.send_request.assert_called_once_with(bytearray.fromhex("00010000000601" + "0300020002"))

    @patch("deye_connector.DeyeConnector")
    def test_write_register_0x12_to_0xa3d4(self, connector):
        # given
        sut = DeyeModbus(DeyeModbusTcp(self.config, connector))
        connector.send_request.return_value = bytearray.fromhex("00010000000601" + "1000120001")

        # when
        success = sut.write_register(0x12, bytearray.fromhex("A3D4"))

        # then
        self.assertTrue(success)
        connector.send_request.assert_called_once_with(bytearray.fromhex("00010000000901" + "100012000102a3d4"))

    @patch("deye_connector.DeyeConnector")
    def test_write_register_uint_0x12_to_0xa3d4(self, connector):
        # given
        sut = DeyeModbus(DeyeModbusTcp(self.config, connector))
        connector.send_request.return_value = bytearray.fromhex("00010000000601" + "1000120001")

        # when
        success = sut.write_register_uint(0x12, 0xA3D4)

        # then
        self.assertTrue(success)
        connector.send_request.assert_called_once_with(bytearray.fromhex("00010000000901" + "100012000102a3d4"))

    @patch("deye_connector.DeyeConnector")
    def test_write_registers_uint_0x12_to_values(self, connector):
        """Test write_registers_uint with multiple values (covers line 89)."""
        # given
        sut = DeyeModbus(DeyeModbusTcp(self.config, connector))
        connector.send_request.return_value = bytearray.fromhex("00010000000601" + "1000120002")

        # when - write 2 uint values starting at register 0x12
        success = sut.write_registers_uint(0x12, [0x00FF, 0xA3D4])

        # then
        self.assertTrue(success)
        connector.send_request.assert_called_once_with(
            bytearray.fromhex("00010000000B01" + "10001200020400ffa3d4")
        )

    @patch("deye_connector.DeyeConnector")
    def test_subsequent_requests_have_distinct_tx_id(self, connector):
        # given
        sut = DeyeModbus(DeyeModbusTcp(self.config, connector))

        # when
        connector.send_request.return_value = bytearray.fromhex("00010000000701" + "0302000a000b")
        reg_values = sut.read_registers(2, 3)

        # then
        connector.send_request.assert_called_once_with(bytearray.fromhex("00010000000601" + "0300020002"))

        # when
        connector.send_request.reset_mock()
        connector.send_request.return_value = bytearray.fromhex("00020000000701" + "0302000a000b")
        reg_values = sut.read_registers(2, 3)

        # then
        connector.send_request.assert_called_once_with(bytearray.fromhex("00020000000601" + "0300020002"))

    # ---- Priority 1: deye_modbus.py error paths (76% -> 95%) ----

    @patch("deye_connector.DeyeConnector")
    def test_read_registers_returns_empty_on_connector_failure(self, connector):
        """Test read_registers() returns {} when connector returns None.

        Covers: line 50-51 (None response path in read_registers).
        Note: The TCP wrapper also filters very short frames (< 8 bytes), so
        the None path is reached via either True None or a frame too short for TCP.
        """
        # given
        sut = DeyeModbus(DeyeModbusTcp(self.config, connector))
        connector.send_request.return_value = None

        # when
        reg_values = sut.read_registers(1, 5)

        # then
        self.assertEqual(reg_values, {})

    @patch("deye_connector.DeyeConnector")
    def test_read_registers_short_frame_returns_empty(self, connector):
        """Test short frame detection in read response parsing.

        Covers: TCP wrapper returns None for frames < 8 bytes, triggering deye_modbus line 50-51.
        Also tests the conceptual path of too-short responses.
        """
        # given - mock returns a 4-byte frame, which is < 8 and triggers TCP error
        sut = DeyeModbus(DeyeModbusTcp(self.config, connector))
        connector.send_request.return_value = bytearray.fromhex("0103")

        # when
        reg_values = sut.read_registers(1, 5)

        # then
        self.assertEqual(reg_values, {})

    @patch("deye_connector.DeyeConnector")
    def test_read_registers_too_short_parsed_frame_returns_empty(self, connector):
        """Test read response parsing catches frame too short after TCP extraction.

        Covers: __parse_modbus_read_holding_registers_response lines 122-124
        (too-short check when extracted frame < expected_frame_data_len + 2).

        Strategy: Send a mock response where TCP extracts more than 8 bytes
        but the actual data portion after the MBAP header is insufficient.
        """
        # given - send an 10-byte response. After TCP strips 7 MBAP bytes,
        # only 3 bytes remain, making extracted data = unit_id(1) + 3 = 4 data bytes
        # For single register: expected_frame_data_len=5, needs ≥ 7 total (5+2 CRC)
        # But TCP extracts 4 data + 2 CRC = 6 < 7 → too short!
        sut = DeyeModbus(DeyeModbusTcp(self.config, connector))
        connector.send_request.return_value = bytearray.fromhex("00010000000501" + "03")

        # when - request single register but data is too short for valid response
        reg_values = sut.read_registers(1, 1)

        # then
        self.assertEqual(reg_values, {})

    @patch("deye_connector.DeyeConnector")
    def test_read_registers_crc_mismatch_returns_empty(self, connector):
        """Test CRC mismatch in read response parsing.

        Covers: __parse_modbus_read_holding_registers_response lines 127-131 (CRC check failure).

        Strategy: Send a mock response where TCP extracts more data bytes than deye_modbus expects.
        This causes deye_modbus to read data bytes (not TCP's CRC) as the "actual" CRC, causing mismatch.
        """
        # given - send a long frame so TCP extracts > expected data length for single-register read
        # Expected data length for 1 register = 5, plus 2 CRC = 7 total
        # By providing more data in mock[7:], deye_modbus reads bytes at [5:7] as "CRC" but they're actually data
        sut = DeyeModbus(DeyeModbusTcp(self.config, connector))
        # mock[7:] has extra registers appended → TCP extracts > 5 bytes → CRC check fails
        connector.send_request.return_value = bytearray.fromhex("00010000000701" + "0302000a000b")

        # when - request single register but response has multiple registers worth of data
        reg_values = sut.read_registers(1, 1)

        # then
        self.assertEqual(reg_values, {})

    @patch("deye_connector.DeyeConnector")
    def test_write_register_connector_none_returns_false(self, connector):
        """Test write_registers returns False when connector sends None (line 109).

        Covers: write_registers method line ~108-109 (connector.send_request returns None).
        """
        # given
        sut = DeyeModbus(DeyeModbusTcp(self.config, connector))
        connector.send_request.return_value = None

        # when
        success = sut.write_register(0x12, bytearray.fromhex("00ff"))

        # then
        self.assertFalse(success)

    @patch("deye_connector.DeyeConnector")
    def test_write_register_short_frame_returns_false(self, connector):
        """Test short write response frame detection in deye_modbus.

        Covers: __parse_modbus_write_holding_register_response lines 154-158 (frame too short).

        Strategy: Send minimal response that passes TCP >= 8 check but extracts to just 4 data bytes
        (unit_id + 3 bytes from mock[7:]). TCP appends 2 CRC = 6 total < 8.
        """
        # given - sends exactly 8 bytes to TCP, but extracted = unit_id(1) + 3 data = 4 + 2 CRC = 6
        sut = DeyeModbus(DeyeModbusTcp(self.config, connector))
        connector.send_request.return_value = bytearray.fromhex("00010000000401" + "10")

        # when
        success = sut.write_register(0x12, bytearray.fromhex("00ff"))

        # then
        self.assertFalse(success)

    @patch("deye_connector.DeyeConnector")
    def test_write_register_crc_mismatch_returns_false(self, connector):
        """Test write response CRC mismatch.

        Covers: __parse_modbus_write_holding_register_response lines 159-165 (CRC check failure).

        Strategy: Send extra data bytes through TCP extraction so deye_modbus reads wrong "CRC" position.
        For write, expected_frame_data_len = 6. If TCP extracts > 6 bytes,
        deye_modbus reads [6:8] as CRC but those are data bytes, not TCP's actual CRC.
        """
        # given - send extra data so extracted frame > 6 bytes → deye_modbus reads wrong position for CRC check
        sut = DeyeModbus(DeyeModbusTcp(self.config, connector))
        # mock[7:] = "100012000100ff" (7 bytes) → extracted = unit_id + 7 = 8 data bytes
        # TCP appends CRC at position 8. deye_modbus reads [6:8] as "CRC" but those are data bytes.
        connector.send_request.return_value = bytearray.fromhex("00010000000801" + "100012000100ff")

        # when
        success = sut.write_register(0x12, bytearray.fromhex("00ff"))

        # then
        self.assertFalse(success)

    @patch("deye_connector.DeyeConnector")
    def test_write_register_address_mismatch_returns_false(self, connector):
        """Test returned address mismatch in write response.

        Covers: __parse_modbus_write_holding_register_response lines 168-172 (address check failure).

        Strategy: Craft an exact 6-byte extracted frame where the address field differs from what we sent.
        Since TCP extracts unit_id + mock[7:] and mock[7:] is exactly 5 bytes, CRC lands at [6:8] correctly.
        Address at [2:4] will be different from our sent value.
        """
        # given - write to register 0x12, but response has address 0x0002
        # mock[7:] = "1000020001" → extracted frame = 01 10 00 02 00 01 (6 bytes data + CRC at [6:8])
        sut = DeyeModbus(DeyeModbusTcp(self.config, connector))
        connector.send_request.return_value = bytearray.fromhex("00010000000601" + "1000020001")

        # when - write to register 0x12 (address 18) but response says address 2
        success = sut.write_register(0x12, bytearray.fromhex("00ff"))

        # then
        self.assertFalse(success)

    @patch("deye_connector.DeyeConnector")
    def test_write_register_count_mismatch_returns_false(self, connector):
        """Test returned register count mismatch in write response.

        Covers: __parse_modbus_write_holding_register_response lines 173-177 (count check failure).

        Strategy: Craft an exact 6-byte extracted frame where the count field differs from what we sent.
        mock[7:] = "1000120002" → count=2 but we wrote 1 register.
        """
        # given - write 1 register, but response says count=2
        sut = DeyeModbus(DeyeModbusTcp(self.config, connector))
        connector.send_request.return_value = bytearray.fromhex("00010000000601" + "1000120002")

        # when
        success = sut.write_register(0x12, bytearray.fromhex("00ff"))

        # then
        self.assertFalse(success)


if __name__ == "__main__":
    unittest.main()
