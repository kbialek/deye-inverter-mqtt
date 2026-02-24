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

# from deye_solar_sell import DeyeSolarSellEventProcessor
from deye_modbus import DeyeModbus
from deye_mqtt import DeyeMqttClient
from deye_config import DeyeConfig, DeyeMqttConfig, DeyeLoggerConfig
from deye_sensor import Sensor, SingleRegisterSensor
from paho.mqtt.client import Client, MQTTMessage
from deye_set_workmode_processor import DeyeWorkmodeEventProcessor

REGISTER_WORKMODE = 142


class TestDeyeWorkmodeEventProcessor(unittest.TestCase):

    def setUp(self):
        self.config = DeyeLoggerConfig(1234567890, "127.0.0.1", 8899)
        self.sensor1 = SingleRegisterSensor(
            "Workmode set",
            REGISTER_WORKMODE,
            1,
            mqtt_topic_suffix="settings/workmode",
            unit="",
            print_format="{:.0f}",
            signed=False,
            groups=["test"],
        )
        self.sensor2 = SingleRegisterSensor(
            "Bad sensor?",
            REGISTER_WORKMODE + 1,
            1,
            mqtt_topic_suffix="settings/workmodee",
            unit="",
            print_format="{:.0f}",
            signed=False,
            groups=["test"],
        )

    @patch("deye_mqtt.DeyeMqttClient")
    @patch("deye_modbus.DeyeModbus")
    def test_init_with_no_sensor(
        self,
        mqtt_client_mock: DeyeMqttClient,
        modbus_mock: DeyeModbus,
    ):
        # given
        sensors = [self.sensor2]
        processor = DeyeWorkmodeEventProcessor(self.config, mqtt_client_mock, sensors, modbus_mock)

        # when
        processor.initialize()

        # then
        mqtt_client_mock.subscribe_command_handler.assert_not_called()

    @patch("deye_mqtt.DeyeMqttClient")
    @patch("deye_modbus.DeyeModbus")
    def test_init_with_required_sensor(
        self,
        mqtt_client_mock: DeyeMqttClient,
        modbus_mock: DeyeModbus,
    ):
        # given
        sensors = [self.sensor1]
        processor = DeyeWorkmodeEventProcessor(self.config, mqtt_client_mock, sensors, modbus_mock)

        # when
        processor.initialize()

        # then
        mqtt_client_mock.subscribe_command_handler.assert_called_once()

    @patch("deye_mqtt.DeyeMqttClient")
    @patch("deye_modbus.DeyeModbus")
    def test_handle_workmode_sellfirst(
        self,
        mqtt_client_mock: DeyeMqttClient,
        modbus_mock: DeyeModbus,
    ):
        # given
        sensors = [self.sensor1, self.sensor2]
        processor = DeyeWorkmodeEventProcessor(self.config, mqtt_client_mock, sensors, modbus_mock)
        processor.initialize()

        # and
        msg = MQTTMessage()
        msg.payload = b"0"

        # when
        processor.handle_command(None, None, msg)

        # then
        modbus_mock.write_register_uint.assert_called_with(REGISTER_WORKMODE, 0)

    @patch("deye_mqtt.DeyeMqttClient")
    @patch("deye_modbus.DeyeModbus")
    def test_handle_workmode_ze_load(
        self,
        mqtt_client_mock: DeyeMqttClient,
        modbus_mock: DeyeModbus,
    ):
        # given
        sensors = [self.sensor1, self.sensor2]
        processor = DeyeWorkmodeEventProcessor(self.config, mqtt_client_mock, sensors, modbus_mock)
        processor.initialize()

        # and
        msg = MQTTMessage()
        msg.payload = b"1"

        # when
        processor.handle_command(None, None, msg)

        # then
        modbus_mock.write_register_uint.assert_called_with(REGISTER_WORKMODE, 1)

    @patch("deye_mqtt.DeyeMqttClient")
    @patch("deye_modbus.DeyeModbus")
    def test_handle_workmode_ze_ct(
        self,
        mqtt_client_mock: DeyeMqttClient,
        modbus_mock: DeyeModbus,
    ):
        # given
        sensors = [self.sensor1, self.sensor2]
        processor = DeyeWorkmodeEventProcessor(self.config, mqtt_client_mock, sensors, modbus_mock)
        processor.initialize()

        # and
        msg = MQTTMessage()
        msg.payload = b"2"

        # when
        processor.handle_command(None, None, msg)

        # then
        modbus_mock.write_register_uint.assert_called_with(REGISTER_WORKMODE, 2)

    @patch("deye_mqtt.DeyeMqttClient")
    @patch("deye_modbus.DeyeModbus")
    def test_handle_workmode_wrong_input_value(
        self,
        mqtt_client_mock: DeyeMqttClient,
        modbus_mock: DeyeModbus,
    ):
        # given
        sensors = [self.sensor1, self.sensor2]
        processor = DeyeWorkmodeEventProcessor(self.config, mqtt_client_mock, sensors, modbus_mock)
        processor.initialize()

        # and
        msg = MQTTMessage()

        for msg_payload in [b"", b"-5", b"1.2", b"100", b"test", b"Enable", b"X"]:
            msg.payload = msg_payload
            with patch.object(processor, "_DeyeWorkmodeEventProcessor__log") as mock_log:
                processor.handle_command(None, None, msg)
            modbus_mock.write_register_uint.assert_not_called()
            mock_log.error.assert_called()

    @patch("deye_mqtt.DeyeMqttClient")
    @patch("deye_modbus.DeyeModbus")
    def test_handle_workmode_write_failure(
        self,
        mqtt_client_mock: DeyeMqttClient,
        modbus_mock: DeyeModbus,
    ):
        # given
        sensors = [self.sensor1]
        processor = DeyeWorkmodeEventProcessor(self.config, mqtt_client_mock, sensors, modbus_mock)
        processor.initialize()

        # Configure modbus mock to return False (failure)
        modbus_mock.write_register_uint.return_value = False

        # and
        msg = MQTTMessage()
        msg.payload = b"1"

        # when
        with patch.object(processor, "_DeyeWorkmodeEventProcessor__log") as mock_log:
            processor.handle_command(None, None, msg)

            # then
            modbus_mock.write_register_uint.assert_called_with(REGISTER_WORKMODE, 1)
            # Verify that an error was logged
            mock_log.error.assert_called()
