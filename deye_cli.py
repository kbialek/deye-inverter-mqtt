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
import sys

from deye_config import DeyeConfig
from deye_connector import DeyeConnector
from deye_modbus import DeyeModbus

config = DeyeConfig.from_env()

Log_Format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

logging.basicConfig(stream=sys.stdout, format=Log_Format, level=logging.FATAL)

log = logging.getLogger('main')

connector = DeyeConnector(config)
modbus = DeyeModbus(config, connector)


def read_register(args):
    reg_address = int(args[0])
    registers = modbus.read_registers(reg_address, reg_address)
    if registers is None:
        print("Error: no registers read")
        sys.exit(1)
    if reg_address not in registers:
        print(f"Error: register {reg_address} not read")
        sys.exit(1)
    reg_bytes = registers[reg_address]
    reg_value_int = int.from_bytes(reg_bytes, 'big')
    low_byte = reg_bytes[1]
    high_byte = reg_bytes[0]
    print(f'int: {reg_value_int}, l: {low_byte}, h: {high_byte}')


def write_register(args):
    if len(args) < 2:
        print("Not enough arguments")
        sys.exit(1)
    reg_address = int(args[0])
    reg_value = int(args[1])
    if modbus.write_register(reg_address, reg_value):
        print("Ok")
    else:
        print("Error")


def main():
    args = sys.argv[1:]
    command = args[0]
    if command == 'r':
        read_register(args[1:])
    elif command == 'w':
        write_register(args[1:])


if __name__ == "__main__":
    main()
