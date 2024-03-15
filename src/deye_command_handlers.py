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
from deye_config import DeyeConfig
from deye_sensor import Sensor
from paho.mqtt.client import Client, MQTTMessage


class DeyeCommandHandler:
    def __init__(self, id: str, config: DeyeConfig, mqtt_client: DeyeMqttClient):
        self.__log = logging.getLogger(DeyeCommandHandler.__name__)
        self.id = id
        self.__config = config
        self.__mqtt_client = mqtt_client

    def initialize(self):
        pass

    def _subscribe(self, mqtt_topic_suffix: str, handler_method):
        self.__mqtt_client.subscribe(f"{self.__config.mqtt.topic_prefix}/{mqtt_topic_suffix}/command", handler_method)

    def _extract_topic_suffix(self, topic: str) -> str | None:
        prefix = f"{self.__config.mqtt.topic_prefix}/"
        suffix = "/command"
        if topic.startswith(prefix) and topic.endswith(suffix):
            return topic.replace(prefix, "").replace(suffix, "")
        else:
            return None


class DeyeActivePowerRegulationCommandHandler(DeyeCommandHandler):
    def __init__(self, config: DeyeConfig, mqtt_client: DeyeMqttClient, modbus: DeyeModbus, sensors: [Sensor]):
        super().__init__("active_power_regulation", config, mqtt_client)
        self.__log = logging.getLogger(DeyeActivePowerRegulationCommandHandler.__name__)
        self.__modbus = modbus
        self.__active_power_regulation_topic_suffix = "settings/active_power_regulation"
        matching_sensors = [s for s in sensors if s.mqtt_topic_suffix == self.__active_power_regulation_topic_suffix]
        if len(matching_sensors) == 0:
            self.__log.error("Active power regulation sensor not found. Enable appropriate settings metric group.")
            return
        elif len(matching_sensors) > 1:
            self.__log.error(
                "Too many active power regulation sensors not found. Check your metric groups configuration."
            )
            return
        self.__active_power_reg_sensor = matching_sensors[0]

    def initialize(self):
        self._subscribe(self.__active_power_regulation_topic_suffix, self.handle_command)

    def handle_command(self, client: Client, userdata, msg: MQTTMessage):
        try:
            active_power_regulation_factor = float(msg.payload)
        except ValueError:
            self.__log.error("Invalid active power regulation value: %s", msg.payload)
            return

        if active_power_regulation_factor > 120:
            self.__log.error("Given active power regulation value is too high: %f", active_power_regulation_factor)
            return

        if active_power_regulation_factor < 0:
            self.__log.error("Given active power regulation value is too low: %f", active_power_regulation_factor)
            return

        self.__log.info("Setting active power regulation to %f", active_power_regulation_factor)
        reg_addr, reg_value = self.__active_power_reg_sensor.write_value(msg.payload).popitem()
        self.__modbus.write_register(reg_addr, reg_value)
