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
from deye_sensor import Sensor

from deye_command_handlers import DeyeCommandHandler, DeyeActivePowerRegulationCommandHandler
from deye_timeofuse_command_handler import DeyeTimeOfUseService


class DeyeMqttSubscriber:
    @staticmethod
    def create(
        config: DeyeConfig, mqtt_client: DeyeMqttClient, sensors: list[Sensor], modbus: DeyeModbus
    ) -> "DeyeMqttSubscriber":
        command_handlers = [
            DeyeActivePowerRegulationCommandHandler(config, mqtt_client, modbus),
            DeyeTimeOfUseService(config, mqtt_client, sensors, modbus),
        ]
        return DeyeMqttSubscriber(config, mqtt_client, modbus, command_handlers)

    def __init__(
        self,
        config: DeyeConfig,
        mqtt_client: DeyeMqttClient,
        modbus: DeyeModbus,
        command_handlers: [DeyeCommandHandler],
    ):
        self.__log = logging.getLogger(DeyeMqttSubscriber.__name__)

        active_command_handlers = [h for h in command_handlers if h.id in config.active_command_handlers]

        if active_command_handlers:
            mqtt_client.connect()
            for command_handler in active_command_handlers:
                command_handler.initialize()
