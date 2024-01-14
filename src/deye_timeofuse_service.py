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
from deye_observation import Observation
from deye_events import DeyeEventProcessor, DeyeEventList, DeyeObservationEvent

from paho.mqtt.client import Client, MQTTMessage


class DeyeTimeOfUseService(DeyeCommandHandler, DeyeEventProcessor):
    def __init__(self, config: DeyeConfig, mqtt_client: DeyeMqttClient, sensors: list[Sensor], modbus: DeyeModbus):
        super().__init__("time_of_use", config, mqtt_client)
        self.__log = logging.getLogger(DeyeTimeOfUseService.__name__)
        self.__sensors = [sensor for sensor in sensors if sensor.mqtt_topic_suffix.startswith("timeofuse")]
        self.__modbus = modbus
        self.__sensor_map: dict[str, Sensor] = {}
        self.__read_state: dict[Sensor, str] = {}
        self.__modifications: dict[Sensor, str] = {}

    def get_id(self):
        return "time_of_use"

    def initialize(self):
        if self.__sensor_map:
            return
        for sensor in self.__sensors:
            self._subscribe(sensor.mqtt_topic_suffix, self.handle_command)
            self.__sensor_map[sensor.mqtt_topic_suffix] = sensor
        self._subscribe("timeofuse/control", self.handle_control_command)

    def handle_command(self, client: Client, userdata, msg: MQTTMessage):
        sensor_topic_suffix = self._extract_topic_suffix(msg.topic)
        if not sensor_topic_suffix or sensor_topic_suffix not in self.__sensor_map:
            return
        sensor = self.__sensor_map[sensor_topic_suffix]
        value = msg.payload.decode("utf8")
        self.__log.debug(f"Received value for '{sensor.name}': {value}")
        self.__modifications[sensor] = value

    def handle_control_command(self, client: Client, userdata, msg: MQTTMessage):
        if msg.payload == b"write":
            self.write_config(dry_run=False)
        elif msg.payload == b"dry-write":
            self.write_config(dry_run=True)
        elif msg.payload == b"reset":
            self.__modifications.clear()
            self.__log.info("TimeOfUse modifications cleared")

    def write_config(self, dry_run: bool):
        if not self.__read_state:
            self.__log.warning("Time-of-use state not yet read from the inverter. Cannot apply config modifications.")
            return
        write_state = self.__read_state | self.__modifications
        self.__modifications = {}
        reg_map: dict[int, bytearray] = {}
        for sensor in write_state:
            reg_map |= sensor.write_value(write_state[sensor])
        self.__write_registers(reg_map, dry_run)

    def __write_registers(self, reg_map: dict[int, bytearray], dry_run: bool) -> None:
        first_reg_addr = min(reg_map)
        last_reg_addr = max(reg_map)
        reg_data = []
        batch_reg_addr = 0
        for reg_addr in range(
            first_reg_addr, last_reg_addr + 2
        ):  # When last reg is not found, the last batch is written
            if reg_addr in reg_map:
                reg_data.append(reg_map[reg_addr])
                if not batch_reg_addr:
                    batch_reg_addr = reg_addr
            elif reg_data:
                self.__log.info(f"Write time-of-use config registers: {batch_reg_addr}: {reg_data}")
                if not dry_run:
                    self.__modbus.write_registers(batch_reg_addr, reg_data)
                batch_reg_addr = 0
                reg_data.clear()

    def process(self, events: DeyeEventList):
        read_state = {}
        observations: list[Observation] = [ev.observation for ev in events if isinstance(ev, DeyeObservationEvent)]
        for observation in observations:
            sensor = observation.sensor
            if sensor in self.__sensors:
                read_state[sensor] = observation.value_as_str()
        self.__read_state = read_state

    @property
    def read_state(self):
        return self.__read_state

    @property
    def modifications(self):
        return self.__modifications
