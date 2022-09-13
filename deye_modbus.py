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
        self.config = config.logger
        self.connector = connector

    def read_registers(self, first_reg: int, last_reg: int) -> dict[int, int]:
        modbus_frame = self.__build_modbus_read_holding_registers_request_frame(first_reg, last_reg)
        req_frame = self.__build_request_frame(modbus_frame)
        resp_frame = self.connector.send_request(req_frame)
        modbus_resp_frame = self.__extract_modbus_response_frame(resp_frame)
        return self.__parse_modbus_read_holding_registers_response(modbus_resp_frame, first_reg, last_reg)

    def write_register(self, reg_address: int, reg_value: int) -> bool:
        modbus_frame = self.__build_modbus_write_holding_register_request_frame(reg_address, reg_value)
        req_frame = self.__build_request_frame(modbus_frame)
        resp_frame = self.connector.send_request(req_frame)
        modbus_resp_frame = self.__extract_modbus_response_frame(resp_frame)
        return self.__parse_modbus_write_holding_register_response(modbus_resp_frame, reg_address, reg_value)

    def __build_request_frame(self, modbus_frame):
        start = bytearray.fromhex('A5')  # start
        length = bytearray.fromhex('1700')  # datalength
        controlcode = bytearray.fromhex('1045')  # controlCode
        inverter_sn_prefix = bytearray.fromhex('0000')  # serial
        datafield = bytearray.fromhex('020000000000000000000000000000')
        modbus_crc = bytearray.fromhex('{:04x}'.format(libscrc.modbus(modbus_frame)))
        modbus_crc.reverse()
        checksum = bytearray.fromhex('00')  # checksum placeholder for outer frame
        end_code = bytearray.fromhex('15')
        inverter_sn = bytearray.fromhex('{:10x}'.format(self.config.serial_number))
        inverter_sn.reverse()
        frame = start + length + controlcode + inverter_sn_prefix + inverter_sn + datafield \
            + modbus_frame + modbus_crc + checksum + end_code

        checksum = 0
        for i in range(1, len(frame) - 2, 1):
            checksum += frame[i] & 255
        frame[len(frame) - 2] = int((checksum & 255))

        return frame

    def __extract_modbus_response_frame(self, frame):
        # 29 - outer frame, 2 - modbus addr and command, 2 - modbus crc
        if not frame or len(frame) < (29 + 4) or frame[0] != 0xa5 or frame[-1] != 0x15:
            self.__log.error("Invalid response frame")
            return None

        return frame[25:-6]

    def __build_modbus_read_holding_registers_request_frame(self, first_reg, last_reg):
        reg_count = last_reg - first_reg + 1
        return bytearray.fromhex('0103{:04x}{:04x}'.format(first_reg, reg_count))

    def __parse_modbus_read_holding_registers_response(self, frame, first_reg, last_reg):
        reg_count = last_reg - first_reg + 1;
        if not frame or len(frame) != 2 + 1 + reg_count * 2:
            return None
        registers = {}
        a = 0
        while a < reg_count:
            p1 = 3 + (a*2)
            p2 = p1 + 2
            registers[a + first_reg] = frame[p1:p2]
            a += 1
        return registers


    def __build_modbus_write_holding_register_request_frame(self, reg_address, reg_value):
        return bytearray.fromhex('0106{:04x}{:04x}'.format(reg_address, reg_value))

    def __parse_modbus_write_holding_register_response(self, frame, reg_address, reg_value):
        if not frame or len(frame) != 6:
            return False
        returned_address = int.from_bytes(frame[2:4], 'big')
        returned_value = int.from_bytes(frame[4:6], 'big')
        if returned_address != reg_address or returned_value != reg_value:
            return False
        return True