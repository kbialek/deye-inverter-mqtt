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

import libscrc

from deye_connector import DeyeConnector


class DeyeModbus:
    """Simplified Modbus over TCP implementation that works with Deye Solar inverter.
    Inspired by https://github.com/jlopez77/DeyeInverter
    """

    def __init__(self, connector: DeyeConnector):
        self.__log = logging.getLogger(DeyeModbus.__name__)
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
        modbus_crc = bytearray.fromhex("{:04x}".format(libscrc.modbus(modbus_frame)))
        modbus_crc.reverse()

        modbus_resp_frame = self.connector.send_request(modbus_frame + modbus_crc)
        if modbus_resp_frame is None:
            return {}
        return self.__parse_modbus_read_holding_registers_response(modbus_resp_frame, first_reg, last_reg)

    def write_register_uint(self, reg_address: int, reg_value: int) -> bool:
        """Write single modbus holding register, assuming the value is an unsigned int

        Args:
            reg_address (int): The address of the register to write
            reg_value (int): The value of the register to write

        Returns:
            bool: True when the write operation was successful, False otherwise
        """
        return self.write_register(reg_address, reg_value.to_bytes(2, "big", signed=False))

    def write_register(self, reg_address: int, reg_value: bytearray) -> bool:
        """Write single modbus holding register

        Args:
            reg_address (int): The address of the register to write
            reg_value (bytearray): The value of the register to write

        Returns:
            bool: True when the write operation was successful, False otherwise
        """
        return self.write_registers(reg_address, [reg_value])

    def write_registers_uint(self, reg_address: int, reg_values: list[int]) -> bool:
        """Write multiple modbus holding registers, assuming the values are unsigned integers.


        Args:
            reg_address (int): The address of the first register to write
            reg_values (list[int]): The values of the registers to write

        Returns:
            bool: True when the write operation was successful, False otherwise
        """
        return self.write_registers(reg_address, [v.to_bytes(2, "big", signed=False) for v in reg_values])

    def write_registers(self, reg_address: int, reg_values: list[bytearray]) -> bool:
        """Write multiple modbus holding registers.


        Args:
            reg_address (int): The address of the first register to write
            reg_values (list[bytearray]): The values of the registers to write

        Returns:
            bool: True when the write operation was successful, False otherwise
        """

        modbus_frame = self.__build_modbus_write_holding_register_request_frame(reg_address, reg_values)
        modbus_crc = bytearray.fromhex("{:04x}".format(libscrc.modbus(modbus_frame)))
        modbus_crc.reverse()

        modbus_resp_frame = self.connector.send_request(modbus_frame + modbus_crc)
        if modbus_resp_frame is None:
            return False
        return self.__parse_modbus_write_holding_register_response(modbus_resp_frame, reg_address, reg_values)

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
        expected_crc = libscrc.modbus(frame[0:expected_frame_data_len])
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

    def __build_modbus_write_holding_register_request_frame(
        self, reg_address: int, reg_values: list[bytearray]
    ) -> bytearray:
        result = bytearray.fromhex("0110{:04x}{:04x}{:02x}".format(reg_address, len(reg_values), len(reg_values) * 2))
        for v in reg_values:
            self.__log.debug(f"Extending request frame with {v.hex()}")
            result.extend(v)
        return result

    def __parse_modbus_write_holding_register_response(
        self, frame: bytes, reg_address: int, reg_values: list[bytearray]
    ) -> bool:
        expected_frame_data_len = 6
        expected_frame_len = 6 + 2  # 2 bytes for crc
        if len(frame) < expected_frame_len:
            self.__log.error(
                f"Wrong response frame length. Expected at least {expected_frame_len} bytes, got {len(frame)}"
            )
            return False
        actual_crc = int.from_bytes(frame[expected_frame_data_len : expected_frame_data_len + 2], "little")
        expected_crc = libscrc.modbus(frame[0:expected_frame_data_len])
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
