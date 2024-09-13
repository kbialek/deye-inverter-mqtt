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
from datetime import datetime

from deye_events import DeyeEventList, DeyeLoggerStatusEvent, DeyeObservationEvent
from deye_observation import Observation
from deye_sensor import AbstractSensor


class FakeSensor(AbstractSensor):
    def __init__(self, name: str, value: float):
        super().__init__(name, groups=["float"], print_format="{:0.1f}")
        self.value = value

    def read_value(self, registers):
        return self.value


class TestDeyeEventList(unittest.TestCase):
    def test_get_status_event(self):
        # Test case when no status event is present in the list
        events_list = DeyeEventList()
        self.assertIsNone(events_list.get_status())

        # Test case when a status event is present in the list
        events_list = DeyeEventList()
        status_event = DeyeLoggerStatusEvent(online=True)
        events_list.append(status_event)
        events_list.append(DeyeObservationEvent(Observation(FakeSensor("Sensor1", 1.1), datetime.now(), 42)))
        self.assertEqual(events_list.get_status(), status_event.online)

    def test_is_offline(self):
        # Test case when no status event is present in the list
        events_list = DeyeEventList()
        self.assertFalse(events_list.is_offline())

        # Test case when a status event is present and it is online
        events_list = DeyeEventList([DeyeLoggerStatusEvent(online=True)])
        self.assertFalse(events_list.is_offline())

        # Test case when a status event is present and it is offline
        events_list = DeyeEventList([DeyeLoggerStatusEvent(online=False)])
        self.assertTrue(events_list.is_offline())

    def test_compare_observation_events_same(self):
        # Test case when the lists are the same, but order changed
        test_sensor_1 = FakeSensor("Sensor1", 1.1)
        test_sensor_2 = FakeSensor("Sensor2", 1.2)
        events_a = DeyeEventList(
            [
                DeyeLoggerStatusEvent(online=True),
                DeyeObservationEvent(Observation(test_sensor_1, datetime.now(), 42.1)),
                DeyeObservationEvent(Observation(test_sensor_2, datetime.now(), 123)),
            ]
        )
        events_b = DeyeEventList(
            [
                DeyeObservationEvent(Observation(test_sensor_2, datetime.now(), 123)),
                DeyeLoggerStatusEvent(online=True),
                DeyeObservationEvent(Observation(test_sensor_1, datetime.now(), 42.1)),
            ]
        )
        self.assertTrue(events_a.compare_observation_events(events_b))

    def test_compare_observation_events_different(self):
        # Test case when the lists are different
        test_sensor_1 = FakeSensor("Sensor1", 1.1)
        test_sensor_2 = FakeSensor("Sensor2", 1.2)
        events_a = DeyeEventList(
            [
                DeyeLoggerStatusEvent(online=True),
                DeyeObservationEvent(Observation(test_sensor_1, datetime.now(), 42.1)),
                DeyeObservationEvent(Observation(test_sensor_2, datetime.now(), 123)),
            ]
        )
        events_b = DeyeEventList(
            [
                DeyeLoggerStatusEvent(online=True),
                DeyeObservationEvent(Observation(test_sensor_1, datetime.now(), 42.2)),
                DeyeObservationEvent(Observation(test_sensor_2, datetime.now(), 123)),
            ]
        )
        self.assertFalse(events_a.compare_observation_events(events_b))

    def test_compare_events_different_logger_index(self):
        events_a = DeyeEventList(logger_index=1)
        events_b = DeyeEventList(logger_index=2)
        self.assertFalse(events_a.compare_observation_events(events_b))

    def test_compare_events_same_logger_index(self):
        events_a = DeyeEventList(logger_index=2)
        events_b = DeyeEventList(logger_index=2)
        self.assertTrue(events_a.compare_observation_events(events_b))
