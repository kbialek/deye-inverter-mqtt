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


class DeyeSolarSellEventProcessor(DeyeEventProcessor):
    """
    Handles "solar sell" parameter modification requests received through MQTT
    """

    def __init__(
        self, logger_config: DeyeLoggerConfig, mqtt_client: DeyeMqttClient, sensors: [Sensor], modbus: DeyeModbus
    ):
        self.__log = logger_config.logger_adapter(logging.getLogger(DeyeSolarSellEventProcessor.__name__))
        self.__logger_config = logger_config
        self.__mqtt_client = mqtt_client
        self.__modbus = modbus
        self.__solar_sell_topic_suffix = "settings/solar_sell"
        self.__sensors = sensors
        self.__solar_sell_sensor_reg_addr = None

    def get_id(self):
        return "solar_sell"

    def get_description(self):
        return "Solar Sell enable/disable over MQTT"

    def initialize(self):
        matching_sensors = [s for s in self.__sensors if s.mqtt_topic_suffix == self.__solar_sell_topic_suffix]
        if len(matching_sensors) == 0:
            self.__log.error("Solar sell sensor not found. Enable appropriate settings metric group.")
            return
        elif len(matching_sensors) > 1:
            self.__log.error("Too many solar sell sensors found. Check your metric groups configuration.")
            return
        self.__solar_sell_sensor_reg_addr = matching_sensors[0].get_registers()[0]
        self.__mqtt_client.subscribe_command_handler(
            self.__logger_config.index, self.__solar_sell_topic_suffix, self.handle_command
        )

    def handle_command(self, client: Client, userdata, msg: MQTTMessage):
        if self.__solar_sell_sensor_reg_addr is None:
            return
        try:
            solar_sell_value = int(msg.payload.decode("utf-8").strip())
        except Exception as e:
            self.__log.error(f"Couldn't decode solar sell value: {msg.payload}, {e}")
            return
        if solar_sell_value not in (0, 1):
            self.__log.error(f"Invalid value for solar sell setting: {solar_sell_value}")
            return
        self.__log.debug(f"Setting solar sell to {solar_sell_value}")
        success = self.__modbus.write_register_uint(self.__solar_sell_sensor_reg_addr, solar_sell_value)
        if success:
            self.__log.info(f"Solar sell updated to {solar_sell_value}")
        else:
            self.__log.error(f"Failed setting solar sell to value: {solar_sell_value}")
