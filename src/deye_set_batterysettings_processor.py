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

import logging

from deye_mqtt import DeyeMqttClient
from deye_modbus import DeyeModbus
from deye_config import DeyeLoggerConfig
from deye_events import DeyeEventProcessor
from deye_sensor import Sensor
from paho.mqtt.client import Client, MQTTMessage


class DeyeBatterySettingsEventProcessor(DeyeEventProcessor):
    """
    Handles "battery settings" parameter modification requests received through MQTT
    """

    def __init__(
        self, logger_config: DeyeLoggerConfig, mqtt_client: DeyeMqttClient, sensors: [Sensor], modbus: DeyeModbus
    ):
        self.__log = logger_config.logger_adapter(logging.getLogger(DeyeBatterySettingsEventProcessor.__name__))
        self.__logger_config = logger_config
        self.__mqtt_client = mqtt_client
        self.__modbus = modbus
        self.__battery_settings_topic_suffix = "settings/battery"   # here is one extra segments for specific setting
        self.__sensors = sensors
        self.__battery_settings_sensor_reg_addresses_dict = {}

    def get_id(self):
        return "battery_settings"

    def get_description(self):
        return "Change Battery settings over MQTT"

    def initialize(self):
        matching_sensors = [s for s in self.__sensors if s.mqtt_topic_suffix.startswith(self.__battery_settings_topic_suffix)]
        if not matching_sensors:
            self.__log.warning("BatterySettings sensors not found. Enable appropriate settings metric group.")
            return
        for sensor in matching_sensors:
            reg = sensor.get_registers()[0]
            self.__battery_settings_sensor_reg_addresses_dict[sensor.mqtt_topic_suffix] = reg
        self.__mqtt_client.subscribe_command_handler(
            self.__logger_config.index, f"{self.__battery_settings_topic_suffix}/+", self.handle_command
        )

    def handle_command(self, client: Client, userdata, msg: MQTTMessage):
        if not self.__battery_settings_sensor_reg_addresses_dict:
            return

        topic_suffix = self.__mqtt_client.extract_command_topic_suffix(self.__logger_config.index, msg.topic)
        if not topic_suffix:
            self.__log.error(f"Could not extract command topic suffix from topic '{msg.topic}'")
            return
        try:
            setting_value = int(msg.payload.decode("utf-8").strip())
        except (ValueError, UnicodeDecodeError) as e:
            self.__log.error(f"Could not decode battery setting value: {msg.payload}, error: {e}")
            return

        # The setting name is the last part of the topic suffix
        # e.g., from "settings/battery/grid_charge" -> "grid_charge"
        setting_name = topic_suffix.split("/")[-1]

        if setting_name == "grid_charge" and setting_value not in (0, 1):
            self.__log.error(f"Invalid value for Battery Setting '{setting_name}': {setting_value}")
            return
        else:
            if setting_value < 0 or setting_value > 200: # Most battery settings are 0-200A
                self.__log.error(f"Invalid value for Battery Setting '{setting_name}': {setting_value}. Expected 0-200.")
                return

        reg_address = self.__battery_settings_sensor_reg_addresses_dict.get(topic_suffix)
        if not reg_address:
            self.__log.error(f"Unknown battery setting '{setting_name}' from topic '{msg.topic}'")
            return

        self.__log.debug(f"Setting Battery Setting '{setting_name}' to {setting_value}")
        success = self.__modbus.write_register_uint(reg_address, setting_value)
        if success:
            self.__log.info(f"Battery Setting '{setting_name}' updated to {setting_value}")
        else:
            self.__log.error(f"Failed to set Battery Setting '{setting_name}' to value: {setting_value}")
