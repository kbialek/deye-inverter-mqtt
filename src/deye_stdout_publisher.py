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
import json

from deye_events import DeyeEvent, DeyeEventProcessor, DeyeObservationEvent, DeyeLoggerStatusEvent
from deye_config import DeyeConfig
from deye_observation import Observation


class DeyeStdoutPublisher(DeyeEventProcessor):
    """
    Publishes events on STDOUT
    """

    def __init__(self, config: DeyeConfig):
        self.__log = logging.getLogger(DeyeStdoutPublisher.__name__)
        self.__config = config

    def initialize(self):
        pass

    def get_id(self):
        return "stdout_publisher"

    def process(self, events: list[DeyeEvent]):
        data = []

        for event in events:
            if isinstance(event, DeyeObservationEvent):
                data.append(self.__handle_observation(event.observation))
            elif isinstance(event, DeyeLoggerStatusEvent):
                data.append({"up": 1 if event.online else 0})
            else:
                self.__log.warn(f"Unsupported event type {event.__class__}")

        print(json.dumps({
            'serial':  str(self.__config.logger.serial_number),
            'address': self.__config.logger.ip_address,
            'port':    self.__config.logger.port,
            'data':    data
        }), flush=True)

    def __handle_observation(self, observation: Observation):
        # # we ignore computed stuff, we leave that to downstream systems
        # if "Computed" in observation.sensor.__class__.__name__:
        #     return

        # TODO: do we want to re-use `mqtt_topic_suffix` here or do we want to
        # infere this information from the sensor's name?
        type = observation.sensor.mqtt_topic_suffix
        value = observation.value

        return {
            type:        value,
            "name":      observation.sensor.name,
            "unit":      observation.sensor.unit,
            "groups":    ",".join(observation.sensor.groups),
            "sensor":    observation.sensor.__class__.__name__,
            "timestamp": observation.timestamp.timestamp(),
        }
