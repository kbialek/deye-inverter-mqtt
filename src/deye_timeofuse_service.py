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
import threading
import time

from deye_io import io_budget, io_lock

from deye_config import DeyeLoggerConfig
from deye_mqtt import DeyeMqttClient
from deye_modbus import DeyeModbus
from deye_sensor import Sensor
from deye_observation import Observation
from deye_events import DeyeEventProcessor, DeyeEventList, DeyeObservationEvent

from paho.mqtt.client import Client, MQTTMessage


class DeyeTimeOfUseService(DeyeEventProcessor):
    def __init__(
        self, logger_config: DeyeLoggerConfig, mqtt_client: DeyeMqttClient, sensors: list[Sensor], modbus: DeyeModbus
    ):
        self.__log = logger_config.logger_adapter(logging.getLogger(DeyeTimeOfUseService.__name__))
        self.__logger_config = logger_config
        self.__mqtt_client = mqtt_client
        self.__sensors = [sensor for sensor in sensors if sensor.mqtt_topic_suffix.startswith("timeofuse")]
        self.__modbus = modbus
        self.__sensor_map: dict[str, Sensor] = {}
        self.__read_state: dict[Sensor, str] = {}
        self.__modifications: dict[Sensor, str] = {}
        self.__state_lock = threading.RLock()
        self.__worker = None
        self.__pending = None
        self.__write_completed_at = None

    def get_id(self):
        return "time_of_use"

    def get_description(self):
        return "Time-of-use configuration over MQTT"

    def initialize(self):
        if self.__sensor_map:
            return
        for sensor in self.__sensors:
            self.__mqtt_client.subscribe_command_handler(
                self.__logger_config.index, sensor.mqtt_topic_suffix, self.handle_command
            )
            self.__sensor_map[sensor.mqtt_topic_suffix] = sensor
        self.__mqtt_client.subscribe_command_handler(
            self.__logger_config.index, "timeofuse/control", self.handle_control_command
        )

    def handle_command(self, client: Client, userdata, msg: MQTTMessage):
        if msg.retain:
            self.__log.warning("Ignoring retained time-of-use command")
            return
        sensor_topic_suffix = self.__mqtt_client.extract_command_topic_suffix(self.__logger_config.index, msg.topic)
        if not sensor_topic_suffix or sensor_topic_suffix not in self.__sensor_map:
            return
        sensor = self.__sensor_map[sensor_topic_suffix]
        value = msg.payload.decode("utf8")
        self.__log.debug("Received value for '%s': %s", sensor.name, value)
        with self.__state_lock:
            self.__modifications[sensor] = value

    def handle_control_command(self, client: Client, userdata, msg: MQTTMessage):
        if msg.retain:
            self.__log.warning("Ignoring retained time-of-use control command")
            return
        with self.__state_lock:
            if msg.payload in (b"write", b"dry-write"):
                # One running request and one replaceable pending request, never an unbounded queue.
                self.__pending = (dict(self.__modifications), msg.payload == b"dry-write")
                self.__modifications.clear()
                if self.__worker is None:
                    self.__worker = threading.Thread(target=self.__run_writer, daemon=True)
                    self.__worker.start()
            elif msg.payload == b"reset":
                self.__modifications.clear()
                self.__pending = None
                self.__log.info("TimeOfUse modifications cleared")

    def __run_writer(self):
        while True:
            with self.__state_lock:
                request = self.__pending
                self.__pending = None
                if request is None:
                    self.__worker = None
                    return
            try:
                self.__apply_config(*request)
            except Exception:
                self.__log.exception("Failed to apply time-of-use configuration")

    def write_config(self, dry_run: bool):
        # Keep the synchronous Python API; MQTT callbacks use the bounded worker above.
        with self.__state_lock:
            modifications = dict(self.__modifications)
            self.__modifications.clear()
        return self.__apply_config(modifications, dry_run)

    def __apply_config(self, modifications: dict[Sensor, str], dry_run: bool):
        attempted = False
        try:
            with io_budget(60), io_lock(self.__modbus.transaction_lock):
                with self.__state_lock:
                    if not self.__sensors or set(self.__read_state) != set(self.__sensors):
                        self.__log.warning("Complete time-of-use state not yet read. Cannot apply modifications.")
                        self.__modbus.request_read()
                        return False
                    write_state = self.__read_state | modifications
                reg_map = {}
                for sensor, value in write_state.items():
                    reg_map.update(sensor.write_value(value))
                attempted = bool(reg_map) and not dry_run
                try:
                    return self.__write_registers(reg_map, dry_run)
                finally:
                    if attempted:
                        # Invalidate even on an uncertain/failed write. Never replay it automatically.
                        with self.__state_lock:
                            self.__read_state = {}
                            self.__write_completed_at = time.monotonic()
        finally:
            if attempted:
                self.__log.info("Time-of-use write finished; requesting physical readback")
                self.__modbus.request_read(confirmation=True)

    def __write_registers(self, reg_map: dict[int, bytearray], dry_run: bool) -> bool:
        if not reg_map:
            self.__log.error("Register map is empty, nothing to write")
            return False
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
                    if not self.__modbus.write_registers(batch_reg_addr, reg_data):
                        self.__log.error("Failed to write time-of-use config registers at %d", batch_reg_addr)
                        return False
                batch_reg_addr = 0
                reg_data.clear()
        return True

    def process(self, events: DeyeEventList):
        read_state = {}
        observations: list[Observation] = [ev.observation for ev in events if isinstance(ev, DeyeObservationEvent)]
        for observation in observations:
            sensor = observation.sensor
            if sensor in self.__sensors:
                read_state[sensor] = observation.value_as_str()
        with self.__state_lock:
            # Publication happens outside the I/O lock. A pre-write read must not overwrite invalidation.
            if self.__write_completed_at is not None and (
                events.read_started_at is None or events.read_started_at < self.__write_completed_at
            ):
                return
            self.__read_state = read_state

    @property
    def read_state(self):
        return self.__read_state

    @property
    def modifications(self):
        return self.__modifications
