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
from unittest.mock import MagicMock, patch

from deye_daemon import DeyeDaemon, DeyeEventList, DeyeLoggerStatusEvent, DeyeObservationEvent, Observation
from deye_sensor import Sensor


class FakeSensor(Sensor):
    def __init__(self, name: str, value: float):
        super().__init__(name, groups=["float"], print_format="{:0.1f}")
        self.value = value

    def read_value(self, registers):
        return self.value


class TestDeyeDaemon(unittest.TestCase):
    def test_no_last_observation(self):
        # Create the DeyeDaemon instance with a mock configuration
        config_mock = MagicMock()
        config_mock.logger.protocol = "tcp"
        daemon = DeyeDaemon(config_mock)
        daemon._DeyeDaemon__config.event_expiry = 360
        # Create some sample events for the test
        observation_1 = DeyeObservationEvent(Observation(FakeSensor("Temperature", 1.1), datetime.now(), 21.2))
        observation_2 = DeyeObservationEvent(Observation(FakeSensor("Humidity", 1.1), datetime.now(), 63.5))
        status_event_online = DeyeLoggerStatusEvent(online=True)
        events_new = DeyeEventList([status_event_online, observation_1, observation_2])
        self.assertTrue(daemon._DeyeDaemon__is_device_observation_changed(events_new))

    def test_is_device_offline(self):
        # Create the DeyeDaemon instance with a mock configuration
        config_mock = MagicMock()
        config_mock.logger.protocol = "tcp"
        daemon = DeyeDaemon(config_mock)
        daemon._DeyeDaemon__config.event_expiry = 360
        # Create some sample events for the test
        observation_1 = DeyeObservationEvent(Observation(FakeSensor("Temperature", 1.1), datetime.now(), 21.2))
        observation_2 = DeyeObservationEvent(Observation(FakeSensor("Humidity", 1.1), datetime.now(), 63.5))
        status_event_online = DeyeLoggerStatusEvent(online=True)
        status_event_offline = DeyeLoggerStatusEvent(online=False)
        daemon._DeyeDaemon__last_observations = DeyeEventList([status_event_online, observation_1, observation_2])
        events_new = DeyeEventList([status_event_offline])
        self.assertFalse(daemon._DeyeDaemon__is_device_observation_changed(events_new))

    @patch("time.time")
    def test_is_evenets_unchanged(self, time):
        # Create the DeyeDaemon instance with a mock configuration
        config_mock = MagicMock()
        config_mock.logger.protocol = "tcp"
        daemon = DeyeDaemon(config_mock)
        daemon._DeyeDaemon__config.event_expiry = 360
        # Create some sample events for the test
        observation_1 = DeyeObservationEvent(Observation(FakeSensor("Temperature", 1.1), datetime.now(), 21.2))
        observation_2 = DeyeObservationEvent(Observation(FakeSensor("Humidity", 1.1), datetime.now(), 63.5))
        status_event_online = DeyeLoggerStatusEvent(online=True)
        daemon._DeyeDaemon__last_observations = DeyeEventList([status_event_online, observation_1, observation_2])

        # Set the initial time for the test
        initial_time = 1628098000
        time.return_value = initial_time

        # Received events are the same as the last published one and within the expiry time
        daemon.__last_observations = DeyeEventList([status_event_online, observation_1, observation_2])
        events_new = DeyeEventList([status_event_online, observation_1, observation_2])
        daemon._DeyeDaemon__event_updated = initial_time - 300  # 5 minutes ago
        self.assertFalse(daemon._DeyeDaemon__is_device_observation_changed(events_new))

    @patch("time.time")
    def test_is_events_unchanged_expired(self, time):
        # Create the DeyeDaemon instance with a mock configuration
        config_mock = MagicMock()
        config_mock.logger.protocol = "tcp"
        daemon = DeyeDaemon(config_mock)
        daemon._DeyeDaemon__config.event_expiry = 360
        # Create some sample events for the test
        observation_1 = DeyeObservationEvent(Observation(FakeSensor("Temperature", 1.1), datetime.now(), 21.2))
        observation_2 = DeyeObservationEvent(Observation(FakeSensor("Humidity", 1.1), datetime.now(), 63.5))
        status_event_online = DeyeLoggerStatusEvent(online=True)
        daemon._DeyeDaemon__last_observations = DeyeEventList([status_event_online, observation_1, observation_2])

        # Set the initial time for the test
        initial_time = 1628098000
        time.return_value = initial_time

        # Received events are the same as the last published one and time expired
        events_new = DeyeEventList([status_event_online, observation_1, observation_2])
        daemon._DeyeDaemon__event_updated = initial_time - 600  # 10 minutes ago
        self.assertTrue(daemon._DeyeDaemon__is_device_observation_changed(events_new))

    def test_is_events_changed(self):
        # Create the DeyeDaemon instance with a mock configuration
        config_mock = MagicMock()
        config_mock.logger.protocol = "tcp"
        daemon = DeyeDaemon(config_mock)
        daemon._DeyeDaemon__config.event_expiry = 360
        # Create some sample events for the test
        observation_1 = DeyeObservationEvent(Observation(FakeSensor("Temperature", 1.1), datetime.now(), 21.2))
        observation_2 = DeyeObservationEvent(Observation(FakeSensor("Humidity", 1.1), datetime.now(), 63.5))
        status_event_online = DeyeLoggerStatusEvent(online=True)
        daemon._DeyeDaemon__last_observations = DeyeEventList([status_event_online, observation_1, observation_2])

        # Received events are different from the last published one (humidity changed)
        events_new = DeyeEventList(
            [
                status_event_online,
                observation_1,
                DeyeObservationEvent(Observation(FakeSensor("Humidity", 1.1), datetime.now(), 63.0)),
            ]
        )
        self.assertTrue(daemon._DeyeDaemon__is_device_observation_changed(events_new))
