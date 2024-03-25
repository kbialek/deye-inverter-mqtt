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

from deye_config import DeyeLoggerConfig
from deye_connector import DeyeConnector


class DeyeModbusTcp:
    """Simplified Modbus over TCP implementation that works with Deye Solar inverter.
    Inspired by https://github.com/jlopez77/DeyeInverter
    """

    def __init__(self, logger_config: DeyeLoggerConfig, connector: DeyeConnector):
        self.__log = logger_config.logger_adapter(logging.getLogger(DeyeModbusTcp.__name__))
        self.loggger_config = logger_config
        self.connector = connector

    def send_request(self, modbus_frame) -> bytes | None:
        req_frame = self.__build_request_frame(modbus_frame)
        resp_frame = self.connector.send_request(req_frame)
        return self.__extract_modbus_response_frame(resp_frame)

    def __build_request_frame(self, modbus_frame) -> bytearray:
        start = bytearray.fromhex("A5")  # start
        length = (13 + len(modbus_frame) + 2).to_bytes(2, "little")  # datalength
        controlcode = bytearray.fromhex("1045")  # controlCode
        inverter_sn_prefix = bytearray.fromhex("0000")  # serial
        datafield = bytearray.fromhex("020000000000000000000000000000")
        checksum = bytearray.fromhex("00")  # checksum placeholder for outer frame
        end_code = bytearray.fromhex("15")
        inverter_sn = bytearray.fromhex("{:10x}".format(self.loggger_config.serial_number))
        inverter_sn.reverse()
        frame = (
            start
            + length
            + controlcode
            + inverter_sn_prefix
            + inverter_sn
            + datafield
            + modbus_frame
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
        if frame[0:3] == b"AT+":
            self.__log.error(
                "AT response detected. Try switching to 'AT' protocol. "
                "Set 'DEYE_LOGGER_PROTOCOL=at' and remove DEYE_LOGGER_PORT from your config"
            )
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

    def __parse_response_error_code(self, frame: bytes) -> None:
        error_frame = frame[25:-2]
        error_code = error_frame[0]
        if error_code == 0x05:
            self.__log.error("Modbus device address does not match.")
        elif error_code == 0x06:
            self.__log.error("Logger Serial Number does not match. Check your configuration file.")
        else:
            self.__log.error("Unknown response error code. Error frame: %s", error_frame.hex())
