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

import unittest
from unittest.mock import patch

from deye_config import DeyeConfig, DeyeLoggerConfig
from deye_modbus import DeyeModbus


class DeyeModbusTest(unittest.TestCase):
    def setUp(self):
        self.config = DeyeConfig(logger_config=DeyeLoggerConfig(1234567890, "192.168.1.1", 8899), mqtt=None)

    @patch("deye_connector.DeyeConnector")
    def test_read_register_0x01(self, connector):
        # given
        sut = DeyeModbus(self.config, connector)
        connector.send_request.return_value = bytearray.fromhex(
            "a5000000000000000000000000000000000000000000000000010301000ac84300000015"
        )

        # when
        reg_values = sut.read_registers(1, 1)

        # then
        self.assertEqual(len(reg_values), 1)
        self.assertTrue(1 in reg_values)
        self.assertEqual(reg_values[1].hex(), "000a")

    @patch("deye_connector.DeyeConnector")
    def test_read_registers_0x02_0x03(self, connector):
        # given
        sut = DeyeModbus(self.config, connector)
        connector.send_request.return_value = bytearray.fromhex(
            "a5000000000000000000000000000000000000000000000000010302000a000b13f600000015"
        )

        # when
        reg_values = sut.read_registers(2, 3)

        # then
        self.assertEqual(len(reg_values), 2)
        self.assertTrue(2 in reg_values)
        self.assertTrue(3 in reg_values)
        self.assertEqual(reg_values[2].hex(), "000a")
        self.assertEqual(reg_values[3].hex(), "000b")

        # and
        connector.send_request.assert_called_once_with(
            bytearray.fromhex("a5170010450000d202964902000000000000000000000000000001030002000265cb5915")
        )

    @patch("deye_connector.DeyeConnector")
    def test_write_register_0x12_to_0xa3d4(self, connector):
        # given
        sut = DeyeModbus(self.config, connector)
        connector.send_request.return_value = bytearray.fromhex(
            "a5000000000000000000000000000000000000000000000000" + "011000120001a1cc" + "0015"
        )

        # when
        success = sut.write_register(0x12, 0xA3D4)

        # then
        self.assertTrue(success)
        connector.send_request.assert_called_once_with(
            bytearray.fromhex("a51a0010450000d202964902000000000000000000000000000001100012000102a3d4dd8d2b15")
        )

    @patch("deye_connector.DeyeConnector")
    def test_read_register_SUN_10K_SG04LP3_EU_part1(self, connector):
        # given
        sut = DeyeModbus(self.config, connector)
        connector.send_request.return_value = bytearray.fromhex(
            "a53b0010150007482ee38d020121d0060091010000403e486301032800ffffff160a12162420ffffffffffffffffffffffffffffffffffff0001ffff0001ffff000003e81fa45115"
        )

        # when
        reg_values = sut.read_registers(0x3C, 0x4F)

        # then
        self.assertEqual(len(reg_values), 20)
        self.assertTrue(0x3C in reg_values)
        self.assertTrue(0x4F in reg_values)
        self.assertEqual(reg_values[0x3C].hex(), "00ff")
        self.assertEqual(reg_values[0x4F].hex(), "03e8")

    @patch("deye_connector.DeyeConnector")
    def test_read_register_SUN_10K_SG04LP3_EU_part2(self, connector):
        # given
        sut = DeyeModbus(self.config, connector)
        connector.send_request.return_value = bytearray.fromhex(
            "a5330010150008482ee38d020122d0060091010000403e486301032000010000ffffffffffff0001ffffffffffffffffffff0000ffff0011ffffffff3a005715"
        )

        # when
        reg_values = sut.read_registers(0x50, 0x5F)

        # then
        self.assertEqual(len(reg_values), 16)
        self.assertTrue(0x50 in reg_values)
        self.assertTrue(0x5F in reg_values)
        self.assertEqual(reg_values[0x50].hex(), "0001")
        self.assertEqual(reg_values[0x5F].hex(), "ffff")

    @patch("deye_connector.DeyeConnector")
    def test_incorrect_inverter_serial_number(self, connector):
        # given
        sut = DeyeModbus(self.config, connector)
        connector.send_request.return_value = bytearray.fromhex(
            "a51000101500c9c22576f80201032d0000790800007106d6630600bd15"
        )

        # when
        with self.assertLogs() as captured:
            sut.read_registers(0x50, 0x5F)

        # then
        self.assertEqual(len(captured.records), 1)
        self.assertEqual(
            captured.records[0].getMessage(), "Logger Serial Number does not match. Check your configuration file."
        )

    @patch("deye_connector.DeyeConnector")
    def test_incorrect_modbus_address(self, connector):
        # given
        sut = DeyeModbus(self.config, connector)
        connector.send_request.return_value = bytearray.fromhex(
            "a51000101500c9c22576f80201032d0000790800007106d6630500bd15"
        )

        # when
        with self.assertLogs() as captured:
            sut.read_registers(0x50, 0x5F)

        # then
        self.assertEqual(len(captured.records), 1)
        self.assertEqual(captured.records[0].getMessage(), "Modbus device address does not match.")

    @patch("deye_connector.DeyeConnector")
    def test_unknown_error_code(self, connector):
        # given
        sut = DeyeModbus(self.config, connector)
        connector.send_request.return_value = bytearray.fromhex(
            "a51000101500c9c22576f80201032d0000790800007106d6630100bd15"
        )

        # when
        with self.assertLogs() as captured:
            sut.read_registers(0x50, 0x5F)

        # then
        self.assertEqual(len(captured.records), 1)
        self.assertEqual(captured.records[0].getMessage(), "Unknown response error code. Error frame: 0100")


if __name__ == "__main__":
    unittest.main()
