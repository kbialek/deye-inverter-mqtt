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

from deye_solar_sell_max_power import DeyeSolarSellMaxPowerEventProcessor
from deye_modbus import DeyeModbus
from deye_mqtt import DeyeMqttClient
from deye_config import DeyeLoggerConfig
from deye_sensor import SingleRegisterSensor
from paho.mqtt.client import MQTTMessage

REGISTER_SOLAR_SELL_MAX_POWER = 340


class TestDeyeSolarSellMaxPowerEventProcessor(unittest.TestCase):

    def setUp(self):
        self.config = DeyeLoggerConfig(1234567890, "127.0.0.1", 8899)
        self.sensor = SingleRegisterSensor(
            "Solar sell max power",
            REGISTER_SOLAR_SELL_MAX_POWER,
            1,
            mqtt_topic_suffix="settings/solar_sell_max_power",
            unit="W",
            print_format="{:.0f}",
            signed=False,
            groups=["test"],
        )
        self.sensor_other = SingleRegisterSensor(
            "Other sensor",
            100,
            1,
            mqtt_topic_suffix="settings/other",
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
        sensors = [self.sensor_other]
        processor = DeyeSolarSellMaxPowerEventProcessor(self.config, mqtt_client_mock, sensors, modbus_mock)

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
        sensors = [self.sensor]
        processor = DeyeSolarSellMaxPowerEventProcessor(self.config, mqtt_client_mock, sensors, modbus_mock)

        # when
        processor.initialize()

        # then
        mqtt_client_mock.subscribe_command_handler.assert_called_once()

    @patch("deye_mqtt.DeyeMqttClient")
    @patch("deye_modbus.DeyeModbus")
    def test_handle_valid_power_value(
        self,
        mqtt_client_mock: DeyeMqttClient,
        modbus_mock: DeyeModbus,
    ):
        # given
        sensors = [self.sensor, self.sensor_other]
        processor = DeyeSolarSellMaxPowerEventProcessor(self.config, mqtt_client_mock, sensors, modbus_mock)
        processor.initialize()

        # and
        msg = MQTTMessage()
        msg.payload = b"5000"

        # when
        processor.handle_command(None, None, msg)

        # then
        modbus_mock.write_register_uint.assert_called_with(REGISTER_SOLAR_SELL_MAX_POWER, 5000)

    @patch("deye_mqtt.DeyeMqttClient")
    @patch("deye_modbus.DeyeModbus")
    def test_handle_minimum_power_value(
        self,
        mqtt_client_mock: DeyeMqttClient,
        modbus_mock: DeyeModbus,
    ):
        # given
        sensors = [self.sensor]
        processor = DeyeSolarSellMaxPowerEventProcessor(self.config, mqtt_client_mock, sensors, modbus_mock)
        processor.initialize()

        # and
        msg = MQTTMessage()
        msg.payload = b"0"

        # when
        processor.handle_command(None, None, msg)

        # then
        modbus_mock.write_register_uint.assert_called_with(REGISTER_SOLAR_SELL_MAX_POWER, 0)

    @patch("deye_mqtt.DeyeMqttClient")
    @patch("deye_modbus.DeyeModbus")
    def test_handle_maximum_power_value(
        self,
        mqtt_client_mock: DeyeMqttClient,
        modbus_mock: DeyeModbus,
    ):
        # given
        sensors = [self.sensor]
        processor = DeyeSolarSellMaxPowerEventProcessor(self.config, mqtt_client_mock, sensors, modbus_mock)
        processor.initialize()

        # and
        msg = MQTTMessage()
        msg.payload = b"12000"

        # when
        processor.handle_command(None, None, msg)

        # then
        modbus_mock.write_register_uint.assert_called_with(REGISTER_SOLAR_SELL_MAX_POWER, 12000)

    @patch("deye_mqtt.DeyeMqttClient")
    @patch("deye_modbus.DeyeModbus")
    def test_handle_out_of_range_value(
        self,
        mqtt_client_mock: DeyeMqttClient,
        modbus_mock: DeyeModbus,
    ):
        # given
        sensors = [self.sensor]
        processor = DeyeSolarSellMaxPowerEventProcessor(self.config, mqtt_client_mock, sensors, modbus_mock)
        processor.initialize()

        # and
        msg = MQTTMessage()

        for msg_payload in [b"-1", b"12001", b"99999"]:
            msg.payload = msg_payload
            modbus_mock.reset_mock()

            # when
            processor.handle_command(None, None, msg)

            # then
            modbus_mock.write_register_uint.assert_not_called()

    @patch("deye_mqtt.DeyeMqttClient")
    @patch("deye_modbus.DeyeModbus")
    def test_handle_invalid_payload(
        self,
        mqtt_client_mock: DeyeMqttClient,
        modbus_mock: DeyeModbus,
    ):
        # given
        sensors = [self.sensor]
        processor = DeyeSolarSellMaxPowerEventProcessor(self.config, mqtt_client_mock, sensors, modbus_mock)
        processor.initialize()

        # and
        msg = MQTTMessage()

        for msg_payload in [b"", b"abc", b"1.5", b"on"]:
            msg.payload = msg_payload
            modbus_mock.reset_mock()

            # when
            processor.handle_command(None, None, msg)

            # then
            modbus_mock.write_register_uint.assert_not_called()


if __name__ == "__main__":
    unittest.main()
