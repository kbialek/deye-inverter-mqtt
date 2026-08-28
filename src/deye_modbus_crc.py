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

"""Pure-Python Modbus CRC-16 implementation.

Replaces the ``libscrc`` C extension with a native Python equivalent.
Uses the standard Modbus CRC-16 parameters: polynomial 0xA001
(bitwise-reversed 0x8005), initial value 0xFFFF.

Example:
    >>> modbus_crc(b"\x01\x03\x00\x02\x00\x02") == 0x6D5B
    True
    >>> modbus_crc_bytes(b"\x01\x03\x00\x02\x00\x02").hex()  # little-endian wire order
    '5b6d'
"""

_CRC_POLY = 0xA001
_CRC_INIT = 0xFFFF


def modbus_crc(data: bytes | bytearray) -> int:
    """Compute the Modbus CRC-16 checksum of ``data``.

    Args:
        data: The frame payload (without the CRC bytes).

    Returns:
        int: The 16-bit CRC value, equivalent to ``libscrc.modbus(data)``.
    """
    crc = _CRC_INIT
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x0001:
                crc = (crc >> 1) ^ _CRC_POLY
            else:
                crc >>= 1
    return crc


def modbus_crc_bytes(data: bytes | bytearray) -> bytearray:
    """Compute the Modbus CRC-16 checksum of ``data`` as two wire-order bytes.

    Returns the CRC little-endian (low byte first), as required on the
    Modbus wire. Equivalent to the ``libscrc`` + reverse pattern:

        crc = bytearray.fromhex("{:04x}".format(modbus_crc(data)))
        crc.reverse()
        return crc
    """
    crc = modbus_crc(data)
    return bytearray.fromhex("{:04x}".format(crc))[::-1]
