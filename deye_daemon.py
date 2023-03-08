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
import sys
import time
import datetime

from deye_config import DeyeConfig
from deye_connector import DeyeConnector
from deye_modbus import DeyeModbus
from deye_sensors import sensor_list, sensor_register_ranges
from deye_mqtt import DeyeMqttClient
from deye_observation import Observation
from deye_events import DeyeEvent, DeyeLoggerStatusEvent, DeyeObservationEvent
from deye_mqtt_publisher import DeyeMqttPublisher


class DeyeDaemon():

    def __init__(self, config: DeyeConfig):
        self.__log = logging.getLogger(DeyeDaemon.__name__)
        self.__config = config
        mqtt_client = DeyeMqttClient(config)
        connector = DeyeConnector(config)
        self.modbus = DeyeModbus(config, connector)
        self.sensors = [s for s in sensor_list if s.in_any_group(self.__config.metric_groups)]
        self.reg_ranges = [r for r in sensor_register_ranges if r.in_any_group(self.__config.metric_groups)]
        self.processors = [
            DeyeMqttPublisher(mqtt_client)
        ]

    def do_task(self):
        self.__log.info("Reading start")
        regs = {}
        for reg_range in self.reg_ranges:
            self.__log.info(f"Reading registers [{reg_range}]")
            regs |= self.modbus.read_registers(reg_range.first_reg_address, reg_range.last_reg_address)
        events: list[DeyeEvent] = []
        events.append(DeyeLoggerStatusEvent(len(regs) > 0))
        events += self.__get_observations_from_reg_values(regs)
        for processor in self.processors:
            processor.process(events)
        self.__log.info("Reading completed")

    def __get_observations_from_reg_values(self, regs: dict[int, int]) -> list[DeyeObservationEvent]:
        timestamp = datetime.datetime.now()
        events = []
        for sensor in self.sensors:
            value = sensor.read_value(regs)
            if value is not None:
                observation = Observation(sensor, timestamp, value)
                events.append(DeyeObservationEvent(observation))
                self.__log.debug(f'{observation.sensor.name}: {observation.value_as_str()}')
        return events


def main():
    config = DeyeConfig.from_env()
    daemon = DeyeDaemon(config)
    while True:
        daemon.do_task()
        time.sleep(config.data_read_inverval)


if __name__ == "__main__":
    main()
