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
import time

from deye_config import DeyeLoggerConfig
from deye_connector import DeyeConnector


class DeyeAtConnector(DeyeConnector):
    def __init__(self, logger_config: DeyeLoggerConfig) -> None:
        self.__log = logger_config.logger_adapter(logging.getLogger(DeyeAtConnector.__name__))
        self.__logger_config = logger_config
        self.__reachable = True

    def __create_socket(self) -> socket.socket | None:
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            client_socket.settimeout(1)
            if not self.__reachable:
                self.__reachable = True
                self.__log.info("Re-connected to socket on IP %s", self.__logger_config.ip_address)
            return client_socket
        except OSError as e:
            if self.__reachable:
                self.__log.warning("Could not open socket on IP %s: %s", self.__logger_config.ip_address, e)
            else:
                self.__log.debug("Could not open socket on IP %s: %s", self.__logger_config.ip_address, e)
            self.__reachable = False
            return

    def __send_at_command(self, client_socket: socket, at_command: str) -> None:
        self.__log.debug("Sending AT command: %s", at_command)
        client_socket.sendto(at_command, (self.__logger_config.ip_address, self.__logger_config.port))
        time.sleep(0.1)

    def __receive_at_response(self, client_socket: socket) -> str:
        attempts = 5
        while attempts > 0:
            attempts = attempts - 1
            try:
                data = client_socket.recv(1024)
                if data:
                    self.__log.debug("Received AT response in %s. attempt: %s", 5 - attempts, data)
                    return data
                self.__log.warning("No data received")
            except socket.timeout:
                self.__log.debug("Connection response timeout")
                if attempts == 0:
                    self.__log.warning("Too many connection timeouts")
            except OSError as e:
                self.__log.error("Connection error: %s: %s", self.__logger_config.ip_address, e)
                return
            except Exception:
                self.__log.exception("Unknown connection error")
                return
        return

    def __authenticate(self, client_socket) -> None:
        self.__send_at_command(client_socket, b"WIFIKIT-214028-READ")
        self.__receive_at_response(client_socket)

    def __deauthenticate(self, client_socket) -> None:
        self.__send_at_command(client_socket, b"AT+Q\n")

    def send_request(self, req_frame) -> bytes | None:
        modbus_response = None
        client_socket = self.__create_socket()

        if client_socket is None:
            return None

        try:
            self.__authenticate(client_socket)
            self.__send_at_command(client_socket, b"+ok")

            modbus_frame_str = req_frame.hex()
            self.__send_at_command(
                client_socket, bytes(f"AT+INVDATA={int(len(modbus_frame_str) / 2)},{modbus_frame_str}\n", "ascii")
            )
            time.sleep(1)
            at_response = self.__receive_at_response(client_socket)
            if not at_response or at_response.startswith(b"+ok=no data"):
                return modbus_response
            if at_response.startswith(b"+ok="):
                modbus_response = DeyeAtConnector.extract_modbus_respose(at_response)
                self.__log.debug("Extracted Modbus response %s", modbus_response.hex())

            self.__deauthenticate(client_socket)
        except Exception:
            self.__log.exception("Failed to read data over AT command")
        finally:
            client_socket.close()

        return modbus_response

    @staticmethod
    def extract_modbus_respose(at_cmd_response: bytes) -> bytes:
        extracted_modus_response = at_cmd_response.replace(b"\x10", b"")[4:-4].decode("utf-8")
        if len(extracted_modus_response) > 4 and extracted_modus_response[-4:] == "0000":
            extracted_modus_response = extracted_modus_response[0:-4]
        return bytearray.fromhex(extracted_modus_response)
