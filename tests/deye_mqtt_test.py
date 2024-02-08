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
from deye_mqtt import DeyeMqttClient
from deye_config import DeyeConfig, DeyeLoggerConfig, DeyeMqttConfig


class TestDeyeMqttClient:
    @staticmethod
    @pytest.fixture
    def logger_config_mock(mocker) -> DeyeLoggerConfig:
        mock = mocker.Mock(spec=DeyeLoggerConfig)
        mock.serial_number = 123
        mock.index = 0
        return mock

    @staticmethod
    @pytest.fixture
    def mqtt_config_mock(mocker) -> DeyeMqttConfig:
        return mocker.Mock(wraps=DeyeMqttConfig(host="", port=0, username="", password="", topic_prefix=""))

    @staticmethod
    @pytest.fixture
    def config_mock(logger_config_mock, mqtt_config_mock) -> DeyeConfig:
        return DeyeConfig(logger_configs=logger_config_mock, mqtt=mqtt_config_mock)

    def test_extract_command_topic_suffix_with_zero_logger_index(self, config_mock, mqtt_config_mock):
        # given
        sut = DeyeMqttClient(config_mock)

        # and
        mqtt_config_mock.topic_prefix = "prefix"

        # when
        result = sut.extract_command_topic_suffix(0, "prefix/foo/command")

        # then
        assert result == "foo"

    def test_extract_command_topic_suffix_with_non_zero_logger_index(self, config_mock, mqtt_config_mock):
        # given
        sut = DeyeMqttClient(config_mock)

        # and
        mqtt_config_mock.topic_prefix = "prefix"

        # when
        result = sut.extract_command_topic_suffix(1, "prefix/1/foo/command")

        # then
        assert result == "foo"
