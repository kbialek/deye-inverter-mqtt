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

from deye_at_connector import DeyeAtConnector
from deye_config import DeyeLoggerConfig
from deye_connector import DeyeConnector
from deye_tcp_connector import DeyeTcpConnector
from deye_modbus_tcp import DeyeModbusTcp


class DeyeConnectorFactory:
    def create_connector(self, logger_config: DeyeLoggerConfig) -> DeyeConnector:
        log = logger_config.logger_adapter(logging.getLogger(DeyeConnectorFactory.__name__))
        protocol = logger_config.protocol
        if protocol == "tcp":
            log.info("Creating Modbus/TCP Logger connector")
            return DeyeModbusTcp(logger_config, DeyeTcpConnector(logger_config))
        elif protocol == "at":
            log.info("Creating Modbus/AT Logger connector")
            return DeyeAtConnector(logger_config)
        else:
            raise Exception(f"Unsupported logger protocol {protocol}")
