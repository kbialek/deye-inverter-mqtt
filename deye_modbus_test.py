import unittest
from unittest.mock import patch

from deye_modbus import DeyeModbus
from deye_config import DeyeConfig, DeyeLoggerConfig


class DeyeModbusTest(unittest.TestCase):

    def setUp(self):
        self.config = DeyeConfig(
            logger_config=DeyeLoggerConfig(12345678, '192.168.1.1', 8899),
            mqtt=None
        )

    @patch('deye_connector.DeyeConnector')
    def test_read_register_0x01(self, connector):
        # given
        sut = DeyeModbus(self.config, connector)
        connector.send_request.return_value = bytearray.fromhex(
            'a5000000000000000000000000000000000000000000000000010301000a000000000015')

        # when
        reg_values = sut.read_registers(1, 1)

        # then
        self.assertEqual(len(reg_values), 1)
        self.assertTrue(1 in reg_values)
        self.assertEqual(reg_values[1].hex(), '000a')

    @patch('deye_connector.DeyeConnector')
    def test_read_registers_0x02_0x03(self, connector):
        # given
        sut = DeyeModbus(self.config, connector)
        connector.send_request.return_value = bytearray.fromhex(
            'a5000000000000000000000000000000000000000000000000010302000a000b000000000015')

        # when
        reg_values = sut.read_registers(2, 3)

        # then
        self.assertEqual(len(reg_values), 2)
        self.assertTrue(2 in reg_values)
        self.assertTrue(3 in reg_values)
        self.assertEqual(reg_values[2].hex(), '000a')
        self.assertEqual(reg_values[3].hex(), '000b')


if __name__ == '__main__':
    unittest.main()
