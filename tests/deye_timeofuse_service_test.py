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

import pytest
from datetime import datetime
from paho.mqtt.client import Client, MQTTMessage

from deye_timeofuse_service import DeyeTimeOfUseService
from deye_events import DeyeEventList, DeyeObservationEvent
from deye_modbus import DeyeModbus
from deye_mqtt import DeyeMqttClient
from deye_config import DeyeConfig, DeyeMqttConfig, DeyeLoggerConfig, DeyeMqttTlsConfig
from deye_observation import Observation
import deye_sensors_deye_sg04lp3

sensor_time_1 = deye_sensors_deye_sg04lp3.deye_sg04lp3_time_of_use_148
sensor_time_2 = deye_sensors_deye_sg04lp3.deye_sg04lp3_time_of_use_149
sensor_time_3 = deye_sensors_deye_sg04lp3.deye_sg04lp3_time_of_use_150


class TestDeyeTimeOfUseService:
    @staticmethod
    @pytest.fixture
    def modbus_mock(mocker) -> DeyeModbus:
        return mocker.Mock(spec=DeyeModbus)

    @staticmethod
    @pytest.fixture
    def mqtt_config_mock(mocker) -> DeyeMqttConfig:
        return mocker.Mock(wraps=DeyeMqttConfig(host="", port=0, username="", password="", topic_prefix=""))

    @staticmethod
    @pytest.fixture
    def logger_config_mock(mocker) -> DeyeLoggerConfig:
        mock = mocker.Mock(spec=DeyeLoggerConfig)
        mock.serial_number = 123
        mock.index = 0
        return mock

    @staticmethod
    @pytest.fixture
    def config_mock(logger_config_mock, mqtt_config_mock) -> DeyeConfig:
        return DeyeConfig(logger_configs=logger_config_mock, mqtt=mqtt_config_mock)

    @staticmethod
    @pytest.fixture
    def mqtt_client_mock(mocker, config_mock) -> DeyeMqttClient:
        return mocker.Mock(wraps=DeyeMqttClient(config_mock))

    def test_process_events_to_build_read_state(self, logger_config_mock, mqtt_client_mock, modbus_mock):
        # given
        sensors = [sensor_time_1, sensor_time_2, sensor_time_3]
        sut = DeyeTimeOfUseService(logger_config_mock, mqtt_client_mock, sensors, modbus_mock)

        # and
        now = datetime.now()
        observations = [
            Observation(sensor_time_1, now, 500),
            Observation(sensor_time_2, now, 700),
            Observation(sensor_time_3, now, 1000),
        ]
        events = []
        for obs in observations:
            events.append(DeyeObservationEvent(obs))

        # when
        sut.process(DeyeEventList(events))

        # then
        assert sut.read_state[sensor_time_1] == "500.0"
        assert sut.read_state[sensor_time_2] == "700.0"
        assert sut.read_state[sensor_time_3] == "1000.0"

    def test_handle_modification_command(self, logger_config_mock, mqtt_client_mock, mqtt_config_mock, modbus_mock):
        # given
        mqtt_config_mock.topic_prefix = "deye"

        # and: do not forward subscribe calls to the wrapped client
        mqtt_client_mock.subscribe_command_handler.return_value = None

        # and
        sensors = [sensor_time_1, sensor_time_2, sensor_time_3]
        sut = DeyeTimeOfUseService(logger_config_mock, mqtt_client_mock, sensors, modbus_mock)
        sut.initialize()

        # and
        assert not sut.modifications

        # when
        msg = MQTTMessage(1, b"deye/timeofuse/time/1/command")
        msg.payload = b"0600"
        sut.handle_command(None, None, msg)

        # then
        assert sut.modifications[sensor_time_1] == "0600"
