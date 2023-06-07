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

# flake8: noqa

import logging
import socket

from deye_config import DeyeConfig


class DeyeConnector:
    def __init__(self, config: DeyeConfig) -> None:
        self.__log = logging.getLogger(DeyeConnector.__name__)
        self.config = config.logger
        self.__reachable = True

    def send_request(self, req_frame) -> bytes | None:
        try:
            client_socket = socket.create_connection((self.config.ip_address, self.config.port), timeout=10)
            if not self.__reachable:
                self.__reachable = True
                self.__log.info("Re-connected to socket on IP %s", self.config.ip_address)
        except OSError as e:
            if self.__reachable:
                self.__log.warning("Could not open socket on IP %s: %s", self.config.ip_address, e)
            else:
                self.__log.debug("Could not open socket on IP %s: %s", self.config.ip_address, e)
            self.__reachable = False
            return

        self.__log.debug("Request frame: %s", req_frame.hex())
        client_socket.sendall(req_frame)

        attempts = 5
        while attempts > 0:
            attempts = attempts - 1
            try:
                data = client_socket.recv(1024)
                if data:
                    self.__log.debug("Received response frame in %s. attempt: %s", 5 - attempts, data.hex())
                    return data
                self.__log.warning("No data received")
            except socket.timeout:
                self.__log.debug("Connection response timeout")
                if attempts == 0:
                    self.__log.warning("Too many connection timeouts")
            except OSError as e:
                self.__log.error("Connection error: %s: %s", self.config.ip_address, e)
                return
            except Exception:
                self.__log.exception("Unknown connection error")
                return

        return
