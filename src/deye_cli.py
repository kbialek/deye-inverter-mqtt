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

import sys
import logging

from deye_config import DeyeConfig
from deye_connector_factory import DeyeConnectorFactory
from deye_modbus import DeyeModbus
from deye_sensors import sensor_list

REGISTER_ADDRESS_MIN = 0
REGISTER_ADDRESS_MAX = 0xFFFF
# Modbus allows at most 125 holding registers in one read response (byte count is a single byte)
MODBUS_MAX_READ_REGISTERS = 125


class DeyeCli:
    def __init__(self, config: DeyeConfig):
        self.__log = logging.getLogger()
        self.__config = config

    def exec_command(self, args):
        logger_config = self.__config.logger
        if args[0].isnumeric():
            logger_index = int(args[0]) - 1
            logger_config = self.__config.logger_configs[logger_index]
            args = args[1:]

        self.__log.info(f"Connecting to logger at IP {logger_config.ip_address}")

        connector = DeyeConnectorFactory().create_connector(logger_config)
        modbus = DeyeModbus(connector)

        command = args[0]
        if command == "r":
            self.read_register(modbus, args[1:], logger_config.max_register_range_length)
        elif command == "w":
            self.write_register(modbus, args[1:])

    def read_register(self, modbus, args, max_range_length: int):
        if not args:
            self.__log.error("Register address is required")
            sys.exit(1)
        reg_address = self.__parse_register_address(args[0])
        if len(args) > 1:
            self.read_register_range(modbus, reg_address, self.__parse_register_address(args[1]), max_range_length)
            return
        registers = modbus.read_registers(reg_address, reg_address)
        if registers is None:
            self.__log.error("Error: no registers read")
            sys.exit(1)
        if reg_address not in registers:
            self.__log.error(f"Error: register {reg_address} not read")
            sys.exit(1)
        reg_bytes = registers[reg_address]
        reg_value_int = int.from_bytes(reg_bytes, "big")
        low_byte = reg_bytes[1]
        high_byte = reg_bytes[0]
        self.__log.info(f"int: {reg_value_int}, l: {low_byte}, h: {high_byte}")

    def read_register_range(self, modbus, first_reg: int, last_reg: int, max_range_length: int):
        """Reads registers first_reg..last_reg in chunks of max_range_length (at most MODBUS_MAX_READ_REGISTERS)
        and prints one line per register: address, value with its hex form, and the name and decoded value of
        the sensors of the configured metric groups that start at this register.

        A chunk that cannot be read is reported and skipped, so a scan across unknown address ranges continues.
        Exits with status 1 only when no register could be read at all.
        """
        if first_reg > last_reg:
            self.__log.error(f"First register {first_reg} must not be greater than last register {last_reg}")
            sys.exit(1)
        chunk_length = max(1, min(max_range_length, MODBUS_MAX_READ_REGISTERS))
        values: dict[int, bytearray] = {}
        failed_chunks = 0
        for chunk_first in range(first_reg, last_reg + 1, chunk_length):
            chunk_last = min(chunk_first + chunk_length - 1, last_reg)
            registers = modbus.read_registers(chunk_first, chunk_last)
            if not registers:
                self.__log.warning(f"Registers {chunk_first}-{chunk_last} not read")
                failed_chunks += 1
                continue
            values.update({r: v for r, v in registers.items() if chunk_first <= r <= chunk_last})
        descriptions = self.__describe_registers(values)
        for reg_address in sorted(values):
            reg_value_int = int.from_bytes(values[reg_address], "big")
            line = f"{reg_address}\t{reg_value_int} (0x{reg_value_int:04x})"
            if reg_address in descriptions:
                line += "\t" + "; ".join(descriptions[reg_address])
            print(line)
        self.__log.info(
            f"Read {len(values)} of {last_reg - first_reg + 1} registers, {failed_chunks} chunk(s) not read"
        )
        if not values:
            sys.exit(1)

    def __describe_registers(self, registers: dict[int, bytearray]) -> dict[int, list[str]]:
        """Decodes the read registers with the sensors of the configured metric groups (DEYE_METRIC_GROUPS).

        Returns "<sensor name>: <value> <unit>" texts keyed by the first register of each sensor whose registers
        were all read.
        """
        active_groups = set(self.__config.metric_groups)
        descriptions: dict[int, list[str]] = {}
        for sensor in sensor_list:
            sensor_registers = sensor.get_registers()
            if not sensor_registers or not sensor.in_any_group(active_groups):
                continue
            if not all(r in registers for r in sensor_registers):
                continue
            try:
                value = sensor.read_value(registers)
                if value is None:
                    continue
                text = f"{sensor.name}: {sensor.format_value(value)}"
            except Exception as e:
                self.__log.debug(f"Cannot decode sensor {sensor.name}: {e}")
                continue
            if sensor.unit:
                text += f" {sensor.unit}"
            descriptions.setdefault(sensor_registers[0], []).append(text)
        return descriptions

    def __parse_register_address(self, arg: str) -> int:
        try:
            reg_address = int(arg)
        except ValueError:
            self.__log.error(f"Invalid register address: {arg}")
            sys.exit(1)
        if reg_address < REGISTER_ADDRESS_MIN or reg_address > REGISTER_ADDRESS_MAX:
            self.__log.error(
                f"Register address {reg_address} out of range {REGISTER_ADDRESS_MIN}-{REGISTER_ADDRESS_MAX}"
            )
            sys.exit(1)
        return reg_address

    def write_register(self, modbus, args):
        if len(args) < 2:
            self.__log.error("Not enough arguments")
            sys.exit(1)
        reg_address = int(args[0])
        reg_value = int(args[1])
        if modbus.write_register_uint(reg_address, reg_value):
            self.__log.info("Ok")
        else:
            self.__log.error("Error")


def main():
    config = DeyeConfig.from_env()
    cli = DeyeCli(config)
    args = sys.argv[1:]
    cli.exec_command(args)


if __name__ == "__main__":
    main()
