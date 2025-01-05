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

from deye_config import DeyeLoggerConfig
from deye_connector import DeyeConnector


class DeyeModbusTcp(DeyeConnector):
    """Canonical ModbusTcp implementation"""

    def __init__(self, logger_config: DeyeLoggerConfig, connector: DeyeConnector):
        self.__log = logger_config.logger_adapter(logging.getLogger(DeyeModbusTcp.__name__))
        self.loggger_config = logger_config
        self.connector = connector
        self.__tx_id = 0

    def send_request(self, modbus_frame: bytearray) -> bytes | None:
        self.__tx_id = (self.__tx_id + 1) % 0xFFFF
        req_frame = self.__build_request_frame(modbus_frame)
        resp_frame = self.connector.send_request(req_frame)
        return self.__extract_modbus_response_frame(modbus_frame[0], resp_frame)

    def __build_request_frame(self, modbus_frame: bytearray) -> bytearray:
        payload = modbus_frame[1:-2]  # modbus frame w/o address and checksum
        mbap_tx_id = bytearray.fromhex("{:04x}".format(self.__tx_id))
        mbap_protocol_id = bytearray.fromhex("0000")
        mbap_payload_length = bytearray.fromhex("{:04x}".format(1 + len(payload)))
        mbap_unit_id = bytearray.fromhex("01")  # hardcoded unitId

        return mbap_tx_id + mbap_protocol_id + mbap_payload_length + mbap_unit_id + payload

    def __extract_modbus_response_frame(self, mb_fn_code: int, frame: bytes | None) -> bytes | None:
        if not frame:
            # Error was already logged in `send_request()` function
            return None
        if len(frame) < 8:
            self.__log.error("Response frame is too short")
            return None

        data_frame = bytearray.fromhex("{:02x}".format(mb_fn_code)) + frame[7:]
        crc = bytearray.fromhex("{:04x}".format(libscrc.modbus(data_frame)))
        crc.reverse()

        return data_frame + crc
