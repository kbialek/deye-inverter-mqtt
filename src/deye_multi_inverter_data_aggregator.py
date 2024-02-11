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
        self.__logger_events: dict[int, DeyeEventList] = dict()
        self.__ac_active_power = 0
        self.__daily_energy = 0

    def get_id(self) -> str:
        return "multi_inverter_data_aggregator"

    def get_description(self) -> str:
        return "Aggregate metrics from multiple inverters"

    def process(self, events: DeyeEventList) -> None:
        self.__logger_events[events.logger_index] = events

    def aggregate(self) -> list[Observation]:
        now = datetime.now()
        aggregated_observations = [
            Observation(
                deye_sensors_aggregated.aggregated_ac_active_power_sensor,
                now,
                sum(
                    self.__get_metrics_for_aggregation(
                        deye_sensors_aggregated.aggregated_ac_active_power_sensor.mqtt_topic_suffix
                    )
                ),
            ),
            Observation(
                deye_sensors_aggregated.aggregated_day_energy_sensor,
                now,
                sum(
                    self.__get_metrics_for_aggregation(
                        deye_sensors_aggregated.aggregated_day_energy_sensor.mqtt_topic_suffix
                    )
                ),
            ),
        ]
        self.__log.debug("Aggregated observations: %s", aggregated_observations)
        return aggregated_observations

    def __get_metrics_for_aggregation(self, topic_suffix: str) -> list[float]:
        values = [self.__get_metric(topic_suffix, events) for events in self.__logger_events.values()]
        return [value for value in values if value is not None]

    def __get_metric(self, topic_suffix: str, events: DeyeEventList) -> float | None:
        for event in events:
            if not isinstance(event, DeyeObservationEvent):
                continue
            observation: Observation = event.observation
            if observation.sensor.mqtt_topic_suffix == topic_suffix:
                return observation.value
        return None
