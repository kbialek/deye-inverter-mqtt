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
from deye_mqtt import DeyeMqttClient
from deye_config import DeyeLoggerConfig
from deye_sensor import SingleRegisterSensor
from paho.mqtt.client import Client, MQTTMessage
from deye_set_batterysettings_processor import DeyeBatterySettingsEventProcessor

REGISTER_GRID_CHARGE = 130
REGISTER_MAX_CHARGE_CURRENT = 108
REGISTER_MAX_DISCHARGE_CURRENT = 109
REGISTER_MAX_GRID_CHARGE_CURRENT = 128


def extract_topic_suffix_side_effect(logger_index, topic):
    prefix = f"deye/{logger_index}/"
    suffix = "/command"
    if topic.startswith(prefix) and topic.endswith(suffix):
        return topic[len(prefix) : -len(suffix)]
    return None


class TestDeyeBatterySettingsEventProcessor(unittest.TestCase):
    def setUp(self):
        self.config = DeyeLoggerConfig(1234567890, "127.0.0.1", 8899)
        self.sensor_grid_charge = SingleRegisterSensor(
            "Grid Charge Enable",
            REGISTER_GRID_CHARGE,
            1,
            mqtt_topic_suffix="settings/battery/grid_charge",
            unit="",
            print_format="{:.0f}",
            signed=False,
            groups=["test"],
        )
        self.sensor_max_charge_current = SingleRegisterSensor(
            "Max Charge Current",
            REGISTER_MAX_CHARGE_CURRENT,
            1,
            mqtt_topic_suffix="settings/battery/maximum_charge_current",
            unit="",
            print_format="{:.0f}",
            signed=False,
            groups=["test"],
        )
        self.sensor_max_discharge_current = SingleRegisterSensor(
            "Maximum battery discharge current",
            REGISTER_MAX_DISCHARGE_CURRENT,
            1,
            mqtt_topic_suffix="settings/battery/maximum_discharge_current",
            unit="",
            print_format="{:.0f}",
            signed=False,
            groups=["test"],
        )
        self.sensor_max_grid_charge_current = SingleRegisterSensor(
            "Max Grid Charge Current",
            REGISTER_MAX_GRID_CHARGE_CURRENT,
            1,
            mqtt_topic_suffix="settings/battery/maximum_grid_charge_current",
            unit="",
            print_format="{:.0f}",
            signed=False,
            groups=["test"],
        )
        self.sensor_other = SingleRegisterSensor(
            "Other Setting",
            144,
            1,
            mqtt_topic_suffix="settings/other/some_setting",
            unit="",
            print_format="{:.0f}",
            signed=False,
            groups=["test"],
        )

    @patch("deye_mqtt.DeyeMqttClient")
    @patch("deye_modbus.DeyeModbus")
    def test_init_with_no_battery_settings_sensor(
        self,
        modbus_mock: DeyeModbus,
        mqtt_client_mock: DeyeMqttClient,
    ):
        # given
        sensors = [self.sensor_other]
        processor = DeyeBatterySettingsEventProcessor(self.config, mqtt_client_mock, sensors, modbus_mock)

        # when
        processor.initialize()

        # then
        mqtt_client_mock.subscribe_command_handler.assert_not_called()

    @patch("deye_mqtt.DeyeMqttClient")
    @patch("deye_modbus.DeyeModbus")
    def test_init_with_battery_settings_sensors(
        self,
        modbus_mock: DeyeModbus,
        mqtt_client_mock: DeyeMqttClient,
    ):
        # given
        sensors = [self.sensor_grid_charge, self.sensor_max_charge_current, self.sensor_other]
        processor = DeyeBatterySettingsEventProcessor(self.config, mqtt_client_mock, sensors, modbus_mock)

        # when
        processor.initialize()

        # then
        mqtt_client_mock.subscribe_command_handler.assert_called_once_with(
            self.config.index, "settings/battery/+", processor.handle_command
        )
        self.assertIn(
            self.sensor_grid_charge.mqtt_topic_suffix,
            processor._DeyeBatterySettingsEventProcessor__battery_settings_sensor_reg_addresses_dict,
        )
        self.assertIn(
            self.sensor_max_charge_current.mqtt_topic_suffix,
            processor._DeyeBatterySettingsEventProcessor__battery_settings_sensor_reg_addresses_dict,
        )
        self.assertNotIn(
            self.sensor_other.mqtt_topic_suffix,
            processor._DeyeBatterySettingsEventProcessor__battery_settings_sensor_reg_addresses_dict,
        )

    @patch("deye_mqtt.DeyeMqttClient")
    @patch("deye_modbus.DeyeModbus")
    def test_handle_grid_charge_on(
        self,
        modbus_mock: DeyeModbus,
        mqtt_client_mock: DeyeMqttClient,
    ):
        # given
        mqtt_client_mock.extract_command_topic_suffix.side_effect = extract_topic_suffix_side_effect
        sensors = [self.sensor_grid_charge]
        processor = DeyeBatterySettingsEventProcessor(self.config, mqtt_client_mock, sensors, modbus_mock)
        processor.initialize()

        # and
        msg = MQTTMessage()
        msg.topic = f"deye/{self.config.index}/settings/battery/grid_charge/command".encode("utf-8")
        msg.payload = b"1"

        # when
        processor.handle_command(None, None, msg)

        # then
        modbus_mock.write_register_uint.assert_called_with(REGISTER_GRID_CHARGE, 1)

    @patch("deye_mqtt.DeyeMqttClient")
    @patch("deye_modbus.DeyeModbus")
    def test_handle_grid_charge_off(
        self,
        modbus_mock: DeyeModbus,
        mqtt_client_mock: DeyeMqttClient,
    ):
        # given
        mqtt_client_mock.extract_command_topic_suffix.side_effect = extract_topic_suffix_side_effect
        sensors = [self.sensor_grid_charge]
        processor = DeyeBatterySettingsEventProcessor(self.config, mqtt_client_mock, sensors, modbus_mock)
        processor.initialize()

        # and
        msg = MQTTMessage()
        msg.topic = f"deye/{self.config.index}/settings/battery/grid_charge/command".encode("utf-8")
        msg.payload = b"0"

        # when
        processor.handle_command(None, None, msg)

        # then
        modbus_mock.write_register_uint.assert_called_with(REGISTER_GRID_CHARGE, 0)

    @patch("deye_mqtt.DeyeMqttClient")
    @patch("deye_modbus.DeyeModbus")
    def test_handle_max_charge_current(
        self,
        modbus_mock: DeyeModbus,
        mqtt_client_mock: DeyeMqttClient,
    ):
        # given
        mqtt_client_mock.extract_command_topic_suffix.side_effect = extract_topic_suffix_side_effect
        sensors = [self.sensor_max_charge_current]
        processor = DeyeBatterySettingsEventProcessor(self.config, mqtt_client_mock, sensors, modbus_mock)
        processor.initialize()

        # and
        msg = MQTTMessage()
        msg.topic = f"deye/{self.config.index}/settings/battery/maximum_charge_current/command".encode("utf-8")
        msg.payload = b"50"

        # when
        processor.handle_command(None, None, msg)

        # then
        modbus_mock.write_register_uint.assert_called_with(REGISTER_MAX_CHARGE_CURRENT, 50)

    @patch("deye_mqtt.DeyeMqttClient")
    @patch("deye_modbus.DeyeModbus")
    def test_handle_battery_settings_wrong_input_value(
        self,
        modbus_mock: DeyeModbus,
        mqtt_client_mock: DeyeMqttClient,
    ):
        # given
        mqtt_client_mock.extract_command_topic_suffix.side_effect = extract_topic_suffix_side_effect
        sensors = [self.sensor_grid_charge, self.sensor_max_charge_current]
        processor = DeyeBatterySettingsEventProcessor(self.config, mqtt_client_mock, sensors, modbus_mock)
        processor.initialize()

        # and
        msg = MQTTMessage()
        msg.topic = f"deye/{self.config.index}/settings/battery/maximum_charge_current/command".encode("utf-8")

        for msg_payload in [b"", b"-5", b"1.2", b"test", b"Enable", b"X"]:
            msg.payload = msg_payload
            modbus_mock.reset_mock()  # Reset mock to ensure previous calls don't affect this iteration
            with patch.object(processor, "_DeyeBatterySettingsEventProcessor__log") as mock_log:
                processor.handle_command(None, None, msg)
            modbus_mock.write_register_uint.assert_not_called()
            mock_log.error.assert_called()

    @patch("deye_mqtt.DeyeMqttClient")
    @patch("deye_modbus.DeyeModbus")
    def test_handle_grid_charge_invalid_value(
        self,
        modbus_mock: DeyeModbus,
        mqtt_client_mock: DeyeMqttClient,
    ):
        # given
        mqtt_client_mock.extract_command_topic_suffix.side_effect = extract_topic_suffix_side_effect
        sensors = [self.sensor_grid_charge]
        processor = DeyeBatterySettingsEventProcessor(self.config, mqtt_client_mock, sensors, modbus_mock)
        processor.initialize()

        # and
        msg = MQTTMessage()
        msg.topic = f"deye/{self.config.index}/settings/battery/grid_charge/command".encode("utf-8")

        for msg_payload in [b"2", b"100", b"-1"]:
            msg.payload = msg_payload
            modbus_mock.reset_mock()
            with patch.object(processor, "_DeyeBatterySettingsEventProcessor__log") as mock_log:
                processor.handle_command(None, None, msg)
            modbus_mock.write_register_uint.assert_not_called()
            mock_log.error.assert_called()

    @patch("deye_mqtt.DeyeMqttClient")
    @patch("deye_modbus.DeyeModbus")
    def test_handle_battery_settings_write_failure(
        self,
        modbus_mock: DeyeModbus,
        mqtt_client_mock: DeyeMqttClient,
    ):
        # given
        mqtt_client_mock.extract_command_topic_suffix.side_effect = extract_topic_suffix_side_effect
        sensors = [self.sensor_max_charge_current]
        processor = DeyeBatterySettingsEventProcessor(self.config, mqtt_client_mock, sensors, modbus_mock)
        processor.initialize()

        # Configure modbus mock to return False (failure)
        modbus_mock.write_register_uint.return_value = False

        # and
        msg = MQTTMessage()
        msg.topic = f"deye/{self.config.index}/settings/battery/maximum_charge_current/command".encode("utf-8")
        msg.payload = b"50"

        # when
        with patch.object(processor, "_DeyeBatterySettingsEventProcessor__log") as mock_log:
            processor.handle_command(None, None, msg)

            # then
            modbus_mock.write_register_uint.assert_called_with(REGISTER_MAX_CHARGE_CURRENT, 50)
            # Verify that an error was logged
            mock_log.error.assert_called()

    @patch("deye_mqtt.DeyeMqttClient")
    @patch("deye_modbus.DeyeModbus")
    def test_handle_battery_settings_unknown_setting(
        self,
        modbus_mock: DeyeModbus,
        mqtt_client_mock: DeyeMqttClient,
    ):
        # given
        mqtt_client_mock.extract_command_topic_suffix.side_effect = extract_topic_suffix_side_effect
        sensors = [self.sensor_grid_charge]
        processor = DeyeBatterySettingsEventProcessor(self.config, mqtt_client_mock, sensors, modbus_mock)
        processor.initialize()

        # and
        msg = MQTTMessage()
        msg.topic = f"deye/{self.config.index}/settings/battery/unknown_setting/command".encode("utf-8")
        msg.payload = b"10"

        # when
        with patch.object(processor, "_DeyeBatterySettingsEventProcessor__log") as mock_log:
            processor.handle_command(None, None, msg)

            # then
            modbus_mock.write_register_uint.assert_not_called()
            mock_log.error.assert_called()
