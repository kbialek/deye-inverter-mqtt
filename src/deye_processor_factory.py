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

from deye_events import DeyeEventProcessor
from deye_config import DeyeConfig
from deye_mqtt import DeyeMqttClient
from deye_modbus import DeyeModbus
from deye_mqtt_publisher import DeyeMqttPublisher
from deye_set_time_processor import DeyeSetTimeProcessor
from deye_timeofuse_service import DeyeTimeOfUseService
from deye_active_power_regulation import DeyeActivePowerRegulationEventProcessor
from deye_sensor import Sensor


class DeyeProcessorFactory:
    def __init__(self, config: DeyeConfig, mqtt_client: DeyeMqttClient):
        self.__log = logging.getLogger(DeyeProcessorFactory.__name__)
        self.__config = config
        self.__mqtt_client = mqtt_client

    def create_processors(self, modbus: DeyeModbus, sensors: list[Sensor]) -> list[DeyeEventProcessor]:
        processors = []
        self.__append_processor(processors, DeyeMqttPublisher(self.__config, self.__mqtt_client))
        self.__append_processor(processors, DeyeSetTimeProcessor(modbus))
        self.__append_processor(processors, DeyeTimeOfUseService(self.__config, self.__mqtt_client, sensors, modbus))
        self.__append_processor(
            processors, DeyeActivePowerRegulationEventProcessor(self.__config, self.__mqtt_client, modbus)
        )

        for p in processors:
            p.initialize()

        return processors

    def __append_processor(self, processors: list[DeyeEventProcessor], processor: DeyeEventProcessor):
        is_processor_active = processor.get_id() in self.__config.active_processors
        self.__log.info(
            'Feature "{}": {}'.format(processor.get_description(), "enabled" if is_processor_active else "disabled")
        )
        if is_processor_active:
            processors.append(processor)
