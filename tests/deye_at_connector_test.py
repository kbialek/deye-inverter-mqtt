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

import unittest

from deye_at_connector import DeyeAtConnector


class DeyeAtConnectorTest(unittest.TestCase):
    def test_extract_modbus_frame_with_trailing_zeros(self):
        # given
        at_cmd_response = (
            b"+ok=01\x1003\x1072\x1001\x1008\x1000\x1000\x1002\x1094\x106C\x106B\x1000"
            b"\x1000\x1000\x1000\x1000\x1000\x1000\x1000\x1000\x1000\x1000\x1000\x1010\x1029\x100F"
            b"\x1067\x1010\x1005\x1009\x1055\x1008\x10E5\x1009\x1040\x1000\x100F\x1000\x100E\x1000"
            b"\x100F\x1013\x1084\x1024\x10DB\x1000\x1000\x1022\x10AA\x1000\x1000\x1002\x10B2\x1000"
            b"\x1000\x1025\x10C2\x1000\x1000\x1002\x10B2\x1000\x1000\x1005\x107B\x1005\x107B\x1000"
            b"\x1004\x1003\x10E8\x1000\x1000\x1000\x1000\x1000\x1000\x1000\x1000\x1000\x1010\x1000"
            b"\x1000\x1000\x1000\x1000\x1000\x1000\x1000\x1000\x1000\x1000\x1000\x1000\x1000\x1000"
            b"\x1000\x1000\x1000\x1000\x1000\x100E\x10FB\x1000\x1016\x1000\x1015\x1000\x1001\x1000"
            b"\x1000\x1000\x1000\x1000\x1000\x1000\x1000\x1057\x1045\x1000\x1000\x10\r\n\r\n"
        )

        # when
        modbus_response = DeyeAtConnector.extract_modbus_respose(at_cmd_response)

        # then
        assert modbus_response == bytearray.fromhex(
            "0103720108000002946C6B00000000000000000000000010290F671005095508E50940000F000E000F13842"
            "4DB000022AA000002B2000025C2000002B20000057B057B000403E800000000000000000010000000000000"
            "00000000000000000000000000000EFB00160015000100000000000000005745"
        )

    def test_extract_modbus_frame_without_trailing_zeros(self):
        # given
        at_cmd_response = (
            b"+ok=01\x1003\x1072\x1000\x101D\x1000\x1000\x1000\x1000\x100F\x10F2\x1000"
            b"\x1000\x1000\x100E\x1000\x100E\x1000\x1000\x1000\x1000\x1007\x10BD\x1000"
            b"\x1000\x1007\x10D1\x1000\x1000\x1009\x1038\x1000\x1000\x1000\x1000\x1000"
            b"\x1001\x1000\x1000\x1000\x1000\x1013\x1088\x1000\x1000\x1000\x1000\x1000"
            b"\x1000\x1000\x1000\x1000\x1000\x1000\x1000\x1001\x1068\x1000\x1000\x1000"
            b"\x1000\x1000\x1000\x1012\x10E8\x1000\x1000\x1000\x1000\x1000\x1000\x1000"
            b"\x1000\x1000\x1000\x1000\x1000\x1000\x1000\x1000\x1000\x1000\x1000\x1000"
            b"\x1000\x1000\x1000\x1000\x1000\x1000\x1000\x1000\x1000\x1000\x1000\x1000"
            b"\x1000\x1000\x1000\x1000\x1000\x1000\x10EA\x1000\x1007\x1000\x10FA\x1000"
            b"\x1007\x1000\x1000\x1000\x1000\x1000\x1000\x1000\x1000\x1058\x10AB\x10\r\n\r\n"
        )

        # when
        modbus_response = DeyeAtConnector.extract_modbus_respose(at_cmd_response)

        # then
        assert modbus_response == bytearray.fromhex(
            "010372001D000000000FF20000000E000E0000000007BD000007D100000938000000000001"
            "000000001388000000000000000000000000016800000000000012E8000000000000000000"
            "00000000000000000000000000000000000000000000000000000000EA000700FA0007000000000000000058AB"
        )
