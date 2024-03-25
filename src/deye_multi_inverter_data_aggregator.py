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
import deye_sensors_aggregated

from datetime import datetime
from deye_events import DeyeEventProcessor, DeyeEventList, DeyeObservationEvent
from deye_observation import Observation


class DeyeMultiInverterDataAggregator(DeyeEventProcessor):
    def __init__(self):
        self.__log = logging.getLogger(DeyeMultiInverterDataAggregator.__name__)
        self.__ac_active_power = dict[int, float]()
        self.__day_energy = dict[int, float]()
        self.__last_aggregation_ts = datetime.now()

    def get_id(self) -> str:
        return "multi_inverter_data_aggregator"

    def get_description(self) -> str:
        return "Aggregate metrics from multiple inverters"

    def process(self, events: DeyeEventList) -> None:
        self.__update_ac_active_power_value(events)
        self.__update_day_energy_value(events)

    def aggregate(self) -> list[Observation]:
        now = datetime.now()
        if now.day != self.__last_aggregation_ts.day:
            self.__reset_state()
        aggregated_observations = [
            Observation(
                deye_sensors_aggregated.aggregated_ac_active_power_sensor,
                now,
                sum(self.__ac_active_power.values()),
            ),
            Observation(
                deye_sensors_aggregated.aggregated_day_energy_sensor,
                now,
                sum(self.__day_energy.values()),
            ),
        ]
        self.__last_aggregation_ts = now
        self.__log.debug("Aggregated observations: %s", aggregated_observations)
        return aggregated_observations

    def __get_metric(self, topic_suffix: str, events: DeyeEventList) -> float | None:
        for event in events:
            if not isinstance(event, DeyeObservationEvent):
                continue
            observation: Observation = event.observation
            if observation.sensor.mqtt_topic_suffix == topic_suffix:
                return observation.value
        return None

    def __update_ac_active_power_value(self, events: DeyeEventList) -> None:
        new_value = self.__get_metric(
            deye_sensors_aggregated.aggregated_ac_active_power_sensor.mqtt_topic_suffix, events
        )
        if new_value is not None:
            self.__ac_active_power[events.logger_index] = new_value

    def __update_day_energy_value(self, events: DeyeEventList) -> None:
        new_value = self.__get_metric(deye_sensors_aggregated.aggregated_day_energy_sensor.mqtt_topic_suffix, events)
        if new_value is not None:
            self.__day_energy[events.logger_index] = new_value

    def __reset_state(self):
        self.__ac_active_power.clear()
        self.__day_energy.clear()
