import libscrc
import logging

from deye_connector import DeyeConnector
from deye_config import DeyeConfig


class DeyeModbus:
    """ Simplified Modbus over TCP implementation that works with Deye Solar inverter.
        Supports only Modbus read-holding-registers function (0x03)
        Inspired by https://github.com/jlopez77/DeyeInverter
    """

    def __init__(self, config: DeyeConfig, connector: DeyeConnector):
        self.__log = logging.getLogger(DeyeModbus.__name__)
        self.config = config.inverter
        self.connector = connector

    def read_registers(self, first_reg: int, last_reg: int) -> dict[int, int]:
        req_frame = self.__build_request_frame(first_reg, last_reg)
        resp_frame = self.connector.send_request(req_frame)
        return self.__parse_response(resp_frame, first_reg, last_reg)

    def __build_request_frame(self, first_reg, last_reg):
        start = bytearray.fromhex('A5')  # start
        length = bytearray.fromhex('1700')  # datalength
        controlcode = bytearray.fromhex('1045')  # controlCode
        inverter_sn_prefix = bytearray.fromhex('0000')  # serial
        datafield = bytearray.fromhex('020000000000000000000000000000')
        reg_count = last_reg - first_reg + 1
        modbus_cmd = bytearray.fromhex('0103{:04x}{:04x}'.format(first_reg, reg_count))
        modbus_crc = bytearray.fromhex('{:04x}'.format(libscrc.modbus(modbus_cmd)))
        modbus_crc.reverse()
        checksum = bytearray.fromhex('00')  # checksum placeholder for outer frame
        end_code = bytearray.fromhex('15')
        inverter_sn = bytearray.fromhex('{:10x}'.format(self.config.serial_number))
        inverter_sn.reverse()
        frame = start + length + controlcode + inverter_sn_prefix + inverter_sn + datafield + modbus_cmd + modbus_crc + checksum + end_code

        checksum = 0
        for i in range(1, len(frame) - 2, 1):
            checksum += frame[i] & 255
        frame[len(frame) - 2] = int((checksum & 255))

        self.__log.debug("Request frame: %s", frame.hex())
        return frame

    def __parse_response(self, frame, first_reg, last_reg):
        self.__log.debug("Response frame: %s", frame.hex())
        registers = {}
        reg_count = last_reg - first_reg + 1
        if not frame or len(frame) != (34 + reg_count * 2) or frame[0] != 0xa5 or frame[-1] != 0x15:
            self.__log.error("Invalid response frame")
            return registers

        a = 0
        while a < reg_count:
            p1 = 28 + (a*2)
            p2 = p1 + 2
            registers[a + first_reg] = frame[p1:p2]
            a += 1
        return registers
