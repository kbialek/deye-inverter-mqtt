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

import pytest

from datetime import datetime

from deye_multi_inverter_data_aggregator import DeyeMultiInverterDataAggregator
from deye_events import DeyeEventList, DeyeObservationEvent
from deye_observation import Observation
from deye_sensors import production_today_sensor, ac_active_power_sensor
from deye_sensors_aggregated import aggregated_ac_active_power_sensor, aggregated_day_energy_sensor


class TestDeyeMultiInverterDataAggregator:
    def test_process_and_aggregate_metrics(self):
        # given
        sut = DeyeMultiInverterDataAggregator()

        # and
        now = datetime.now()

        # and
        events_1 = DeyeEventList(
            events=[
                DeyeObservationEvent(Observation(ac_active_power_sensor, now, 1.2)),
                DeyeObservationEvent(Observation(production_today_sensor, now, 1.3)),
            ],
            logger_index=1,
        )

        events_2 = DeyeEventList(
            events=[
                DeyeObservationEvent(Observation(ac_active_power_sensor, now, 1.4)),
                DeyeObservationEvent(Observation(production_today_sensor, now, 1.5)),
            ],
            logger_index=2,
        )

        # when
        sut.process(events_1)
        sut.process(events_2)
        observations = sut.aggregate()

        # then
        assert len(observations) == 2

        # and
        for observation in observations:
            if observation.sensor == aggregated_ac_active_power_sensor:
                assert observation.value == pytest.approx(2.6)
            elif observation.sensor == aggregated_day_energy_sensor:
                assert observation.value == pytest.approx(2.8)
            else:
                assert False

    def test_retain_missing_metrics(self):
        # given
        sut = DeyeMultiInverterDataAggregator()

        # and
        now = datetime.now()

        # and
        events_1 = DeyeEventList(
            events=[
                DeyeObservationEvent(Observation(ac_active_power_sensor, now, 1.2)),
                DeyeObservationEvent(Observation(production_today_sensor, now, 1.3)),
            ],
            logger_index=1,
        )

        events_2 = DeyeEventList(
            events=[
                DeyeObservationEvent(Observation(ac_active_power_sensor, now, 1.4)),
            ],
            logger_index=1,
        )

        # when
        sut.process(events_1)
        sut.process(events_2)
        observations = sut.aggregate()

        # then
        assert len(observations) == 2

        # and
        for observation in observations:
            if observation.sensor == aggregated_ac_active_power_sensor:
                assert observation.value == pytest.approx(1.4)
            elif observation.sensor == aggregated_day_energy_sensor:
                assert observation.value == pytest.approx(1.3)
            else:
                assert False
