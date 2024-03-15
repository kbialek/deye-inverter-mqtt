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
from deye_config import DeyeConfig, DeyeLoggerConfig
from deye_mqtt import DeyeMqttClient
from deye_modbus import DeyeModbus
from deye_mqtt_publisher import DeyeMqttPublisher
from deye_set_time_processor import DeyeSetTimeProcessor
from deye_timeofuse_service import DeyeTimeOfUseService
from deye_active_power_regulation import DeyeActivePowerRegulationEventProcessor
from deye_sensor import Sensor
from deye_plugin_loader import DeyePluginContext, DeyePluginLoader
from deye_multi_inverter_data_aggregator import DeyeMultiInverterDataAggregator


class DeyeProcessorFactory:
    def __init__(self, config: DeyeConfig, mqtt_client: DeyeMqttClient):
        self.__log = logging.getLogger(DeyeProcessorFactory.__name__)
        self.__config = config
        self.__mqtt_client = mqtt_client
        self.__first_run = True
        plugin_context = DeyePluginContext(config, mqtt_client)
        self.plugin_loader = DeyePluginLoader(config)
        self.plugin_loader.load_plugins(plugin_context)

    def create_processors(
        self, logger_config: DeyeLoggerConfig, modbus: DeyeModbus, sensors: list[Sensor]
    ) -> list[DeyeEventProcessor]:
        processors = (
            self.__create_builtin_processors(logger_config, modbus, sensors) + self.plugin_loader.get_event_processors()
        )
        for p in processors:
            p.initialize()
        self.__first_run = False
        return processors

    def __create_builtin_processors(
        self, logger_config: DeyeLoggerConfig, modbus: DeyeModbus, sensors: list[Sensor]
    ) -> list[DeyeEventProcessor]:
        processors = []
        self.__append_processor(processors, DeyeMqttPublisher(logger_config, self.__mqtt_client))
        self.__append_processor(processors, DeyeSetTimeProcessor(logger_config, modbus))
        self.__append_processor(processors, DeyeTimeOfUseService(logger_config, self.__mqtt_client, sensors, modbus))
        self.__append_processor(
            processors, DeyeActivePowerRegulationEventProcessor(logger_config, self.__mqtt_client, sensors, modbus)
        )
        return processors

    def create_multi_inverter_data_aggregator(self) -> DeyeMultiInverterDataAggregator:
        return DeyeMultiInverterDataAggregator()

    def create_aggregating_processors(self, logger_config: DeyeLoggerConfig) -> list[DeyeEventProcessor]:
        processors = self.__create_builtin_aggregating_processors(logger_config)
        for p in processors:
            p.initialize()
        return processors

    def __create_builtin_aggregating_processors(self, logger_config: DeyeLoggerConfig) -> list[DeyeEventProcessor]:
        processors = []
        self.__append_processor(processors, DeyeMqttPublisher(logger_config, self.__mqtt_client))
        return processors

    def __append_processor(self, processors: list[DeyeEventProcessor], processor: DeyeEventProcessor):
        is_processor_active = processor.get_id() in self.__config.active_processors
        if self.__first_run:
            self.__log.info(
                'Feature "{}": {}'.format(processor.get_description(), "enabled" if is_processor_active else "disabled")
            )
        if is_processor_active:
            processors.append(processor)
