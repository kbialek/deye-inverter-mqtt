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
from deye_modbus_tcp import DeyeModbusTcp


class DeyeModbusTcpTest(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
