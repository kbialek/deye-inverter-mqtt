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
            self.read_register(modbus, args[1:])
        elif command == "w":
            self.write_register(modbus, args[1:])

    def read_register(self, modbus, args):
        reg_address = int(args[0])
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
