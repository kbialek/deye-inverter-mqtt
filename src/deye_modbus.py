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

from deye_config import DeyeConfig
from deye_connector import DeyeConnector


class DeyeModbus:
    """Simplified Modbus over TCP implementation that works with Deye Solar inverter.
    Inspired by https://github.com/jlopez77/DeyeInverter
    """

    def __init__(self, config: DeyeConfig, connector: DeyeConnector):
        self.__log = logging.getLogger(DeyeModbus.__name__)
        self.config = config.logger
        self.connector = connector

    def read_registers(self, first_reg: int, last_reg: int) -> dict[int, bytearray]:
        """Reads multiple modbus holding registers

        Args:
            first_reg (int): The address of the first register to read
            last_reg (int): The address of the last register to read

        Returns:
            dict[int, bytearray]: Map of register values, where the register address is the map key,
            and register value is the map value
        """
        modbus_frame = self.__build_modbus_read_holding_registers_request_frame(first_reg, last_reg)
        req_frame = self.__build_request_frame(modbus_frame)
        resp_frame = self.connector.send_request(req_frame)
        modbus_resp_frame = self.__extract_modbus_response_frame(resp_frame)
        if modbus_resp_frame is None:
            return {}
        return self.__parse_modbus_read_holding_registers_response(modbus_resp_frame, first_reg, last_reg)

    def write_register(self, reg_address: int, reg_value: int) -> bool:
        """Write single modbus holding register

        Args:
            reg_address (int): The address of the register to write
            reg_value (int): The value of the register to write

        Returns:
            bool: True when the write operation was successful, False otherwise
        """
        return self.write_registers(reg_address, [reg_value])

    def write_registers(self, reg_address: int, reg_values: list[int]) -> bool:
        """Write multiple modbus holding registers.


        Args:
            reg_address (int): The address of the first register to write
            reg_values (list[int]): The values of the registers to write

        Returns:
            bool: True when the write operation was successful, False otherwise
        """

        modbus_frame = self.__build_modbus_write_holding_register_request_frame(reg_address, reg_values)
        req_frame = self.__build_request_frame(modbus_frame)
        resp_frame = self.connector.send_request(req_frame)
        modbus_resp_frame = self.__extract_modbus_response_frame(resp_frame)
        if modbus_resp_frame is None:
            return False
        return self.__parse_modbus_write_holding_register_response(modbus_resp_frame, reg_address, reg_values)

    def __build_request_frame(self, modbus_frame) -> bytearray:
        start = bytearray.fromhex("A5")  # start
        length = (15 + len(modbus_frame) + 2).to_bytes(2, "little")  # datalength
        controlcode = bytearray.fromhex("1045")  # controlCode
        inverter_sn_prefix = bytearray.fromhex("0000")  # serial
        datafield = bytearray.fromhex("020000000000000000000000000000")
        modbus_crc = self.crc16(modbus_frame)
        checksum = bytearray.fromhex("00")  # checksum placeholder for outer frame
        end_code = bytearray.fromhex("15")
        inverter_sn = bytearray.fromhex("{:10x}".format(self.config.serial_number))
        inverter_sn.reverse()
        frame = (
            start
            + length
            + controlcode
            + inverter_sn_prefix
            + inverter_sn
            + datafield
            + modbus_frame
            + modbus_crc
            + checksum
            + end_code
        )

        checksum = 0
        for i in range(1, len(frame) - 2, 1):
            checksum += frame[i] & 255
        frame[len(frame) - 2] = int((checksum & 255))

        return frame

    def __extract_modbus_response_frame(self, frame: bytes | None) -> bytes | None:
        # 29 - outer frame, 2 - modbus addr and command, 2 - modbus crc
        if not frame:
            # Error was already logged in `send_request()` function
            return None
        if len(frame) == 29:
            self.__parse_response_error_code(frame)
            return None
        if len(frame) < (29 + 4):
            self.__log.error("Response frame is too short")
            return None
        if frame[0] != 0xA5:
            self.__log.error("Response frame has invalid starting byte")
            return None
        if frame[-1] != 0x15:
            self.__log.error("Response frame has invalid ending byte")
            return None

        return frame[25:-2]

    def __build_modbus_read_holding_registers_request_frame(self, first_reg: int, last_reg: int) -> bytearray:
        reg_count = last_reg - first_reg + 1
        return bytearray.fromhex("0103{:04x}{:04x}".format(first_reg, reg_count))

    def __parse_modbus_read_holding_registers_response(
        self, frame: bytes, first_reg: int, last_reg: int
    ) -> dict[int, bytearray]:
        reg_count = last_reg - first_reg + 1
        registers = {}
        expected_frame_data_len = 2 + 1 + reg_count * 2
        if len(frame) < expected_frame_data_len + 2:  # 2 bytes for crc
            self.__log.error("Modbus frame is too short")
            return registers
        actual_crc = int.from_bytes(frame[expected_frame_data_len : expected_frame_data_len + 2], "little")
        expected_crc = int.from_bytes(self.crc16(frame[0:expected_frame_data_len]), "little")
        if actual_crc != expected_crc:
            self.__log.error(
                "Modbus frame crc is not valid. Expected {:04x}, got {:04x}".format(expected_crc, actual_crc)
            )
            return registers
        a = 0
        while a < reg_count:
            p1 = 3 + (a * 2)
            p2 = p1 + 2
            registers[a + first_reg] = frame[p1:p2]
            a += 1
        return registers

    def __build_modbus_write_holding_register_request_frame(self, reg_address: int, reg_values: list[int]) -> bytearray:
        return bytearray.fromhex(
            "0110{:04x}{:04x}{:02x}{}".format(
                reg_address, len(reg_values), len(reg_values) * 2, "".join(["{:04x}".format(v) for v in reg_values])
            )
        )

    def __parse_modbus_write_holding_register_response(
        self, frame: bytes, reg_address: int, reg_values: list[int]
    ) -> bool:
        expected_frame_data_len = 6
        expected_frame_len = 6 + 2  # 2 bytes for crc
        if len(frame) < expected_frame_len:
            self.__log.error(
                f"Wrong response frame length. Expected at least {expected_frame_len} bytes, got {len(frame)}"
            )
            return False
        actual_crc = int.from_bytes(frame[expected_frame_data_len : expected_frame_data_len + 2], "little")
        expected_crc = int.from_bytes(self.crc16(frame[0:expected_frame_data_len]), "little")
        if actual_crc != expected_crc:
            self.__log.error(
                "Modbus frame crc is not valid. Expected {:04x}, got {:04x}".format(expected_crc, actual_crc)
            )
            return False
        returned_address = int.from_bytes(frame[2:4], "big")
        returned_count = int.from_bytes(frame[4:6], "big")
        if returned_address != reg_address:
            self.__log.error(
                f"Returned address does not match sent value. Expected {reg_address}, got {returned_address}"
            )
            return False
        if returned_count != len(reg_values):
            self.__log.error(
                f"Returned register count does not match sent value. Expected {len(reg_values)}, got {returned_count}"
            )
            return False
        return True

    def __parse_response_error_code(self, frame: bytes) -> None:
        error_frame = frame[25:-2]
        error_code = error_frame[0]
        if error_code == 0x05:
            self.__log.error("Modbus device address does not match.")
        elif error_code == 0x06:
            self.__log.error("Logger Serial Number does not match. Check your configuration file.")
        else:
            self.__log.error("Unknown response error code. Error frame: %s", error_frame.hex())

    def crc16(self, data: bytes) -> bytes:
        """Calculate CRC-16 for Modbus, taken from https://pypi.org/project/modbus-crc
        Copyright (c) 2023, Alexey Kuznetsov"""
        crc_high = 0xFF
        crc_low = 0xFF
        LOW_BYTES = b'\
\x00\xC0\xC1\x01\xC3\x03\x02\xC2\xC6\x06\x07\xC7\x05\xC5\xC4\x04\
\xCC\x0C\x0D\xCD\x0F\xCF\xCE\x0E\x0A\xCA\xCB\x0B\xC9\x09\x08\xC8\
\xD8\x18\x19\xD9\x1B\xDB\xDA\x1A\x1E\xDE\xDF\x1F\xDD\x1D\x1C\xDC\
\x14\xD4\xD5\x15\xD7\x17\x16\xD6\xD2\x12\x13\xD3\x11\xD1\xD0\x10\
\xF0\x30\x31\xF1\x33\xF3\xF2\x32\x36\xF6\xF7\x37\xF5\x35\x34\xF4\
\x3C\xFC\xFD\x3D\xFF\x3F\x3E\xFE\xFA\x3A\x3B\xFB\x39\xF9\xF8\x38\
\x28\xE8\xE9\x29\xEB\x2B\x2A\xEA\xEE\x2E\x2F\xEF\x2D\xED\xEC\x2C\
\xE4\x24\x25\xE5\x27\xE7\xE6\x26\x22\xE2\xE3\x23\xE1\x21\x20\xE0\
\xA0\x60\x61\xA1\x63\xA3\xA2\x62\x66\xA6\xA7\x67\xA5\x65\x64\xA4\
\x6C\xAC\xAD\x6D\xAF\x6F\x6E\xAE\xAA\x6A\x6B\xAB\x69\xA9\xA8\x68\
\x78\xB8\xB9\x79\xBB\x7B\x7A\xBA\xBE\x7E\x7F\xBF\x7D\xBD\xBC\x7C\
\xB4\x74\x75\xB5\x77\xB7\xB6\x76\x72\xB2\xB3\x73\xB1\x71\x70\xB0\
\x50\x90\x91\x51\x93\x53\x52\x92\x96\x56\x57\x97\x55\x95\x94\x54\
\x9C\x5C\x5D\x9D\x5F\x9F\x9E\x5E\x5A\x9A\x9B\x5B\x99\x59\x58\x98\
\x88\x48\x49\x89\x4B\x8B\x8A\x4A\x4E\x8E\x8F\x4F\x8D\x4D\x4C\x8C\
\x44\x84\x85\x45\x87\x47\x46\x86\x82\x42\x43\x83\x41\x81\x80\x40'

        HIGH_BYTES = b'\
\x00\xC1\x81\x40\x01\xC0\x80\x41\x01\xC0\x80\x41\x00\xC1\x81\x40\
\x01\xC0\x80\x41\x00\xC1\x81\x40\x00\xC1\x81\x40\x01\xC0\x80\x41\
\x01\xC0\x80\x41\x00\xC1\x81\x40\x00\xC1\x81\x40\x01\xC0\x80\x41\
\x00\xC1\x81\x40\x01\xC0\x80\x41\x01\xC0\x80\x41\x00\xC1\x81\x40\
\x01\xC0\x80\x41\x00\xC1\x81\x40\x00\xC1\x81\x40\x01\xC0\x80\x41\
\x00\xC1\x81\x40\x01\xC0\x80\x41\x01\xC0\x80\x41\x00\xC1\x81\x40\
\x00\xC1\x81\x40\x01\xC0\x80\x41\x01\xC0\x80\x41\x00\xC1\x81\x40\
\x01\xC0\x80\x41\x00\xC1\x81\x40\x00\xC1\x81\x40\x01\xC0\x80\x41\
\x01\xC0\x80\x41\x00\xC1\x81\x40\x00\xC1\x81\x40\x01\xC0\x80\x41\
\x00\xC1\x81\x40\x01\xC0\x80\x41\x01\xC0\x80\x41\x00\xC1\x81\x40\
\x00\xC1\x81\x40\x01\xC0\x80\x41\x01\xC0\x80\x41\x00\xC1\x81\x40\
\x01\xC0\x80\x41\x00\xC1\x81\x40\x00\xC1\x81\x40\x01\xC0\x80\x41\
\x00\xC1\x81\x40\x01\xC0\x80\x41\x01\xC0\x80\x41\x00\xC1\x81\x40\
\x01\xC0\x80\x41\x00\xC1\x81\x40\x00\xC1\x81\x40\x01\xC0\x80\x41\
\x01\xC0\x80\x41\x00\xC1\x81\x40\x00\xC1\x81\x40\x01\xC0\x80\x41\
\x00\xC1\x81\x40\x01\xC0\x80\x41\x01\xC0\x80\x41\x00\xC1\x81\x40'

        for byte in data:
            index = crc_high ^ int(byte)
            crc_high = crc_low ^ HIGH_BYTES[index]
            crc_low = LOW_BYTES[index]

        return bytes([crc_high, crc_low])
