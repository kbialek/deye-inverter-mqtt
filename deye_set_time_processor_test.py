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
from unittest.mock import patch

from deye_modbus import DeyeModbus
from deye_set_time_processor import DeyeSetTimeProcessor
from deye_events import DeyeLoggerStatusEvent

class DeyeSetTimeProcessorTest(unittest.TestCase):

    @patch('deye_modbus.DeyeModbus')
    def test_set_time_when_logger_is_becoming_online(self, modbus):
        # given
        processor = DeyeSetTimeProcessor(modbus)

        # when
        processor.process([DeyeLoggerStatusEvent(True)])

        # then
        modbus.write_register.assert_any_call(22, unittest.mock.ANY)
        modbus.write_register.assert_any_call(23, unittest.mock.ANY)
        modbus.write_register.assert_any_call(24, unittest.mock.ANY)

    @patch('deye_modbus.DeyeModbus')
    def test_dont_set_time_when_logger_is_already_online(self, modbus):
        # given
        processor = DeyeSetTimeProcessor(modbus)

        # and
        processor.process([DeyeLoggerStatusEvent(True)])
        modbus.reset_mock()

        # when
        processor.process([DeyeLoggerStatusEvent(True)])

        # then
        modbus.write_register.assert_not_called()
