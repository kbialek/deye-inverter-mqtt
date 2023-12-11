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

from deye_config import DeyeConfig
from deye_mqtt import DeyeMqttClient
from deye_modbus import DeyeModbus
from deye_command_handlers import DeyeCommandHandler
from deye_sensor import Sensor

from paho.mqtt.client import Client, MQTTMessage


class DeyeTimeOfUseCommandHandler(DeyeCommandHandler):
    def __init__(self, config: DeyeConfig, mqtt_client: DeyeMqttClient, sensors: list[Sensor], modbus: DeyeModbus):
        super().__init__("time_of_use", config, mqtt_client)
        self.__log = logging.getLogger(DeyeTimeOfUseCommandHandler.__name__)
        self.__sensors = [sensor for sensor in sensors if sensor.mqtt_topic_suffix.startswith("timeofuse")]
        self.__modbus = modbus

    def initialize(self):
        for sensor in self.__sensors:
            self._subscribe(sensor.mqtt_topic_suffix, self.handle_command)

    def handle_command(self, client: Client, userdata, msg: MQTTMessage):
        pass
