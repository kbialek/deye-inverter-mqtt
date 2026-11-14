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

"""Strict Modbus for the new executor only; uses the bridge's existing connector."""


def crc16(data):
    crc = 0xFFFF
    for value in data:
        crc ^= value
        for _ in range(8):
            crc = (crc >> 1) ^ (0xA001 if crc & 1 else 0)
    return crc


def frame(payload):
    return payload + crc16(payload).to_bytes(2, "little")


class StrictModbus:
    def __init__(self, existing, unit_id=None):
        self.existing = existing
        self.unit_id = existing.modbus_id if unit_id is None else unit_id
        if type(self.unit_id) is not int or not 1 <= self.unit_id <= 247:
            raise ValueError("invalid_modbus_unit")
        self.connector = existing.connector
        self.transaction_lock = existing.transaction_lock
        self.read_requested = getattr(existing, "read_requested", None)
        self.confirmation_read_requested = getattr(existing, "confirmation_read_requested", None)
        self.last_read_error = None

    def _reject_read(self, reason):
        # Fixed categories only; never retain frame bytes or logger identifiers.
        self.last_read_error = reason
        return {}

    def read_registers(self, first, last):
        count = last - first + 1
        if not 1 <= count <= 64:
            raise ValueError("invalid_register_count")
        with self.transaction_lock:
            self.last_read_error = None
            payload = bytes((self.unit_id, 3)) + first.to_bytes(2, "big") + count.to_bytes(2, "big")
            response = self.connector.send_request(frame(payload))
            if not response:
                return self._reject_read("transport_or_outer_frame")
            if len(response) >= 2 and response[1] & 0x80:
                return self._reject_read("modbus_exception")
            if len(response) != 5 + 2 * count:
                return self._reject_read("response_length")
            if response[0] != self.unit_id:
                return self._reject_read("response_unit")
            if response[1] != 3:
                return self._reject_read("response_function")
            if response[2] != 2 * count:
                return self._reject_read("response_byte_count")
            if crc16(response[:-2]) != int.from_bytes(response[-2:], "little"):
                return self._reject_read("response_crc")
            return {first + n: response[3 + n * 2 : 5 + n * 2] for n in range(count)}

    def write_register_uint(self, address, value):
        # No arbitrary write API; defense in depth around the typed executor.
        if address not in (230, 232, 244) or type(value) is not int or not 0 <= value <= 65535:
            raise ValueError("write_not_allowed")
        with self.transaction_lock:
            payload = (
                bytes((self.unit_id, 16)) + address.to_bytes(2, "big") + b"\x00\x01\x02" + value.to_bytes(2, "big")
            )
            response = self.connector.send_request(frame(payload))
            expected = frame(bytes((self.unit_id, 16)) + address.to_bytes(2, "big") + b"\x00\x01")
            return response == expected

    def request_read(self, confirmation=False):
        request = getattr(self.existing, "request_read", None)
        if callable(request):
            request(confirmation=confirmation)
        else:
            if confirmation and self.confirmation_read_requested is not None:
                self.confirmation_read_requested.set()
            if self.read_requested is not None:
                self.read_requested.set()
