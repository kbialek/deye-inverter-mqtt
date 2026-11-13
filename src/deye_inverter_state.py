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

import datetime
import logging
import time

from deye_io import io_budget, io_lock, io_timeout

from deye_config import DeyeConfig, DeyeLoggerConfig
from deye_events import DeyeEventList, DeyeLoggerStatusEvent, DeyeObservationEvent, DeyeEventProcessor
from deye_modbus import DeyeModbus
from deye_observation import Observation
from deye_sensor import SensorRegisterRanges, Sensor


class DeyeInverterState:
    def __init__(
        self,
        config: DeyeConfig,
        logger_config: DeyeLoggerConfig,
        reg_ranges: SensorRegisterRanges,
        modbus: DeyeModbus,
        sensors: list[Sensor],
        processors: list[DeyeEventProcessor],
        read_timeout: float = 60,
    ):
        self.__log = logger_config.logger_adapter(logging.getLogger(DeyeInverterState.__name__))
        self.__config = config
        self.__logger_config = logger_config
        self.__reg_ranges = reg_ranges
        self.__modbus = modbus
        self.__sensors = sensors
        self.__processors = processors
        self.__read_timeout = read_timeout
        self.__needs_publication = True
        self.__last_observations = DeyeEventList(logger_index=logger_config.index)
        self.__event_updated = time.time()

    def read_from_logger(self) -> bool:
        started = time.monotonic()
        read_started = None
        regs = {}
        responded = False
        complete = False
        force_publish = False
        try:
            with io_budget(self.__read_timeout), io_lock(self.__modbus.transaction_lock):
                read_started = time.monotonic()
                force_publish = self.__modbus.confirmation_read_requested.is_set()
                if force_publish:
                    self.__modbus.confirmation_read_requested.clear()
                for reg_range in self.__reg_ranges.ranges:
                    io_timeout(self.__read_timeout)
                    self.__log.info("Reading registers [%s]", reg_range)
                    block = self.__modbus.read_registers(reg_range.first_reg_address, reg_range.last_reg_address)
                    responded |= bool(block)
                    io_timeout(self.__read_timeout)
                    expected = set(range(reg_range.first_reg_address, reg_range.last_reg_address + 1))
                    if set(block) != expected:
                        raise ValueError("Incomplete register block")
                    regs.update(block)
                complete = True
        except (OSError, ValueError) as exc:
            self.__log.warning("Acquisition incomplete: %s", exc)
            regs.clear()
        completed = time.monotonic()
        events = DeyeEventList(logger_index=self.__logger_config.index)
        events.read_started_at = read_started
        events.read_completed_at = completed
        events.append(DeyeLoggerStatusEvent(responded))
        observations = self.__get_observations_from_reg_values(regs) if complete else []
        ready = complete and self.__is_data_ready(observations)
        if ready:
            events += observations
        if not ready:
            self.__needs_publication = True
        # Failures, first recovery and post-write readback must reach processors, even with unchanged values.
        if (
            not ready
            or force_publish
            or self.__needs_publication
            or not self.__config.publish_on_change
            or self.__is_device_observation_changed(events)
        ):
            for processor in self.__processors:
                processor.process(events)
            if ready:
                self.__needs_publication = False
                self.__last_observations = events
                self.__event_updated = time.time()
        self.__log.info("Acquisition complete=%s ready=%s duration=%.3fs", complete, ready, completed - started)
        return ready

    def __get_observations_from_reg_values(self, regs: dict[int, bytearray]) -> list[DeyeObservationEvent]:
        timestamp = datetime.datetime.now()
        events = []
        for sensor in self.__sensors:
            value = sensor.read_value(regs)
            if value is not None:
                observation = Observation(sensor, timestamp, value)
                events.append(DeyeObservationEvent(observation))
                self.__log.debug(f"{observation.sensor.name}: {observation.value_as_str()}")
        return events

    def __is_device_observation_changed(self, events: DeyeEventList) -> bool:
        """Check if the received event observations have changed compared to last published

        Parameters
        ----------
        events : list[DeyeEvent]
            Received event list

        Returns
        -------
        bool
            True if received observation events are different from last published ones
        """
        if events.is_offline():
            self.__log.debug("No observation events received (offline)")
            return False
        if events.compare_observation_events(self.__last_observations):
            self.__log.debug("Event data is unchanged")
            if self.__event_updated + self.__config.event_expiry > time.time():
                self.__log.debug("Event data hasn't expired")
                return False
            else:
                self.__log.info("Event data has expired")
        self.__log.debug("Time since previous update: %s", time.time() - self.__event_updated)
        self.__log.debug("New event data: %s", [str(e) for e in events])
        self.__event_updated = time.time()
        self.__last_observations = events
        return True

    def __is_data_ready(self, observation_events: list[DeyeObservationEvent]) -> bool:
        readiness_check_observations = [
            event.observation for event in observation_events if event.observation.sensor.is_readiness_check
        ]
        self.__log.debug(f"Data readiness observations: {readiness_check_observations}")
        expected = {sensor for sensor in self.__sensors if sensor.is_readiness_check}
        actual = {observation.sensor for observation in readiness_check_observations}
        return expected == actual and all(o.value != 0 for o in readiness_check_observations)
