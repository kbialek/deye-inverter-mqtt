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

from deye_set_time_processor import DeyeSetTimeProcessor
from deye_events import DeyeEventList, DeyeLoggerStatusEvent
from deye_config import DeyeLoggerConfig
import deye_sensors_deye_sg01hp3

datetime_sensor_1 = deye_sensors_deye_sg01hp3.deye_sg01hp3_system_time_62
datetime_sensor_2 = deye_sensors_deye_sg01hp3.deye_sg01hp3_system_time_62


class DeyeSetTimeProcessorTest(unittest.TestCase):
    def setUp(self):
        self.config = DeyeLoggerConfig(1234567890, "192.168.1.1", 8899)

    @patch("deye_modbus.DeyeModbus")
    def test_set_time__when_logger_is_becoming_online_and_no_datetime_sensors_defined(self, modbus):
        # given
        sensors = []
        processor = DeyeSetTimeProcessor(self.config, 300, sensors, modbus)

        # when
        with patch.object(processor, "_DeyeSetTimeProcessor__log") as mock_log:
            processor.process(DeyeEventList([DeyeLoggerStatusEvent(True)]))

        # then
        modbus.write_registers_uint.assert_any_call(22, unittest.mock.ANY)
        mock_log.warning.assert_called_with(
            "Couldn't determine the DateTimeSensor object. Using registers 22-24. "
            "If setting of the time fails, please ensure there's a DateTimeSensor "
            "defined for your inverter in the metric groups."
        )

        # and
        self.assertTrue(processor.last_status)

    @patch("deye_modbus.DeyeModbus")
    def test_keep_stored_status_set_to_offline__when_modbus_write_fails_and_no_datetime_sensors_defined(self, modbus):
        # given
        sensors = []
        processor = DeyeSetTimeProcessor(self.config, 300, sensors, modbus)

        # and
        modbus.write_registers_uint.return_value = False

        # when
        with patch.object(processor, "_DeyeSetTimeProcessor__log") as mock_log:
            processor.process(DeyeEventList([DeyeLoggerStatusEvent(True)]))

        # then
        modbus.write_registers_uint.assert_any_call(22, unittest.mock.ANY)
        mock_log.warning.assert_called()

        # and
        self.assertFalse(processor.last_status)

    @patch("deye_modbus.DeyeModbus")
    def test_set_time__when_logger_is_becoming_online_and_datetime_sensor_defined(self, modbus):
        # given
        sensors = [datetime_sensor_1]
        processor = DeyeSetTimeProcessor(self.config, 300, sensors, modbus)

        # when
        processor.process(DeyeEventList([DeyeLoggerStatusEvent(True)]))

        # then
        modbus.write_registers.assert_any_call(datetime_sensor_1.get_registers()[0], unittest.mock.ANY)
        modbus.write_registers_uint.assert_not_called()

        # and
        self.assertTrue(processor.last_status)

    @patch("deye_modbus.DeyeModbus")
    def test_keep_stored_status_set_to_offline__when_modbus_write_fails_and_datetime_sensor_defined(self, modbus):
        # given
        sensors = [datetime_sensor_1]
        processor = DeyeSetTimeProcessor(self.config, 300, sensors, modbus)

        # and
        modbus.write_registers.return_value = False

        # when
        with patch.object(processor, "_DeyeSetTimeProcessor__log") as mock_log:
            processor.process(DeyeEventList([DeyeLoggerStatusEvent(True)]))

        # then
        modbus.write_registers.assert_any_call(datetime_sensor_1.get_registers()[0], unittest.mock.ANY)
        modbus.write_registers_uint.assert_not_called()
        mock_log.warning.assert_called_with("Failed to set logger time")

        # and
        self.assertFalse(processor.last_status)

    @patch("deye_modbus.DeyeModbus")
    def test_set_time__when_logger_is_becoming_online_and_multiple_datetime_sensors_defined(self, modbus):
        # given
        sensors = [datetime_sensor_1, datetime_sensor_2]
        processor = DeyeSetTimeProcessor(self.config, 300, sensors, modbus)

        # when
        with patch.object(processor, "_DeyeSetTimeProcessor__log") as mock_log:
            processor.process(DeyeEventList([DeyeLoggerStatusEvent(True)]))

        # then
        modbus.write_registers.assert_not_called()
        modbus.write_registers_uint.assert_not_called()
        mock_log.warning.assert_called()

        # and
        self.assertFalse(processor.last_status)
