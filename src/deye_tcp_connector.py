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
import threading
import time

from deye_io import IoBudgetExpired, io_lock, io_timeout

from deye_connector import DeyeConnector
from deye_config import DeyeLoggerConfig

# One lock per (ip, port), shared by every connector talking to that endpoint. Entries are never removed on
# purpose: the endpoints come from the logger config, so the set is small and fixed for the life of the
# process, and dropping a lock while a connector still holds it would let two exchanges overlap.
_endpoint_locks: dict[tuple[str, int], threading.Lock] = {}
_endpoint_locks_guard = threading.Lock()


def _endpoint_lock(ip_address: str, port: int) -> threading.Lock:
    """Returns the lock shared by all connectors talking to the given TCP endpoint"""
    with _endpoint_locks_guard:
        return _endpoint_locks.setdefault((ip_address, port), threading.Lock())


class DeyeTcpConnector(DeyeConnector):
    def __init__(self, logger_config: DeyeLoggerConfig) -> None:
        self.__log = logger_config.logger_adapter(logging.getLogger(DeyeTcpConnector.__name__))
        self.__logger_config = logger_config
        self.__reachable = True
        # Polling and MQTT commands share this connector for one inverter, and several loggers
        # may share one endpoint (e.g. inverters with different Modbus IDs behind one Modbus gateway).
        # Keep the socket exchange, including close, inside the same lock for the endpoint.
        self.__request_lock = _endpoint_lock(logger_config.ip_address, logger_config.port)

    def send_request(self, req_frame) -> bytes | None:
        started = time.monotonic()
        try:
            with io_lock(self.__request_lock, maximum=10):
                return self.__send_request(req_frame)
        except (OSError, ValueError):
            self.__log.warning("TCP exchange failed after %.3fs", time.monotonic() - started, exc_info=True)
            return None

    def __send_request(self, req_frame) -> bytes | None:
        try:
            client_socket = socket.create_connection(
                (self.__logger_config.ip_address, self.__logger_config.port), timeout=io_timeout(10)
            )
            if not self.__reachable:
                self.__reachable = True
                self.__log.info("Re-connected to socket on IP %s", self.__logger_config.ip_address)
        except OSError as e:
            log = self.__log.warning if self.__reachable else self.__log.debug
            log("Could not open socket on IP %s: %s", self.__logger_config.ip_address, e)
            self.__reachable = False
            return None

        with client_socket:
            client_socket.settimeout(io_timeout(10))
            self.__log.debug("Request frame: %s", req_frame.hex())
            # Send once. A missing acknowledgement does not make a write safe to repeat.
            client_socket.sendall(req_frame)
            response_deadline = time.monotonic() + 10
            data = bytearray()
            while True:
                remaining = response_deadline - time.monotonic()
                if remaining <= 0:
                    raise IoBudgetExpired("TCP response deadline expired")
                client_socket.settimeout(io_timeout(remaining))
                try:
                    fragment = client_socket.recv(1024)
                except OSError:
                    raise
                except Exception:
                    self.__log.exception("Unknown connection error")
                    return None
                if not fragment:
                    self.__log.warning("Connection closed before a complete response")
                    return None
                data.extend(fragment)
                expected = self.__response_length(data)
                if expected is None:
                    continue
                if len(data) > expected:
                    raise ValueError("TCP response exceeds its declared frame length")
                if len(data) == expected:
                    self.__log.debug("Received response frame: %s", data.hex())
                    return bytes(data)

    def __response_length(self, data: bytearray) -> int | None:
        if self.__logger_config.protocol == "mbtcp":
            if len(data) < 6:
                return None
            length = int.from_bytes(data[4:6], "big") + 6
            if not 8 <= length <= 260:
                raise ValueError("Invalid Modbus/TCP response length")
            return length
        if data[0] != 0xA5:
            # Preserve the protocol adapter's diagnostics for AT or other invalid replies.
            return len(data)
        if len(data) < 3:
            return None
        length = int.from_bytes(data[1:3], "little") + 13
        if not 13 <= length <= 4096:
            raise ValueError("Invalid logger response length")
        return length
