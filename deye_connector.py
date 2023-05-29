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
import socket

from deye_config import DeyeConfig


class DeyeConnector:
    def __init__(self, config: DeyeConfig) -> None:
        self.__log = logging.getLogger(DeyeConnector.__name__)
        self.config = config.logger

    def send_request(self, req_frame) -> bytes | None:
        for res in socket.getaddrinfo(self.config.ip_address, self.config.port, socket.AF_INET, socket.SOCK_STREAM):
            family, socktype, proto, canonname, sockadress = res
            try:
                client_socket = socket.socket(family, socktype, proto)
                client_socket.settimeout(10)
                client_socket.connect(sockadress)
            except OSError as e:
                self.__log.error("Could not open socket on IP %s: %s", self.config.ip_address, e.strerror)
                return

            self.__log.debug("Request frame: %s", req_frame.hex())
            client_socket.sendall(req_frame)

            attempts = 5
            while attempts > 0:
                attempts = attempts - 1
                try:
                    data = client_socket.recv(1024)
                    if data:
                        self.__log.debug("Response frame: %s", data.hex())
                        return data
                    self.__log.warning("No data received")
                except socket.timeout:
                    self.__log.debug("Connection response timeout")
                    if attempts == 0:
                        self.__log.warning("Too many connection timeouts")
                except OSError as e:
                    self.__log.error("Connection error: %s", e.strerror)
                    return
                except Exception:
                    self.__log.exception("Unknown connection error")
                    return

        return
