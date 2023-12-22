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
from paho.mqtt.client import Client, MQTTMessage


class DeyeCommandHandler:
    def __init__(self, id: str, mqtt_topic_suffix: str, handler_method):
        self.__log = logging.getLogger(DeyeCommandHandler.__name__)
        self.id = id
        self.__mqtt_topic_suffix = mqtt_topic_suffix
        self.__handler_method = handler_method

    def initialize(self, config: DeyeConfig, mqtt_client: DeyeMqttClient):
        mqtt_client.subscribe(f"{config.mqtt.topic_prefix}/{self.__mqtt_topic_suffix}/command", self.__handler_method)


class DeyeActivePowerRegulationCommandHandler(DeyeCommandHandler):
    def __init__(self, modbus: DeyeModbus):
        super().__init__("active_power_regulation", "settings/active_power_regulation", self.handle_command)
        self.__log = logging.getLogger(DeyeActivePowerRegulationCommandHandler.__name__)
        self.__modbus = modbus

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
        self.__modbus.write_register_uint(40, int(active_power_regulation_factor * 10))
