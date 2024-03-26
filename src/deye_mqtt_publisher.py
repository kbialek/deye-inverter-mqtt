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

from deye_events import DeyeEventList, DeyeEventProcessor, DeyeLoggerStatusEvent, DeyeObservationEvent
from deye_mqtt import DeyeMqttClient, DeyeMqttPublishError
from deye_config import DeyeLoggerConfig


class DeyeMqttPublisher(DeyeEventProcessor):
    """
    Publishes events over MQTT.
    """

    def __init__(self, logger_config: DeyeLoggerConfig, mqtt_client: DeyeMqttClient):
        self.__log = logger_config.logger_adapter(logging.getLogger(DeyeMqttPublisher.__name__))
        self.__mqtt_client = mqtt_client

    def initialize(self):
        self.__mqtt_client.connect()

    def get_id(self):
        return "mqtt_publisher"

    def get_description(self):
        return "Report metrics over MQTT"

    def process(self, events: DeyeEventList):
        for event in events:
            try:
                if isinstance(event, DeyeObservationEvent):
                    self.__mqtt_client.publish_observation(event.observation, events.logger_index)
                elif isinstance(event, DeyeLoggerStatusEvent):
                    self.__mqtt_client.publish_logger_status(event.online, events.logger_index)
                else:
                    self.__log.warning(f"Unsupported event type {event.__class__}")
            except DeyeMqttPublishError as e:
                self.__log.error(e.message)
                break

    def get_mqtt_client(self) -> DeyeMqttClient:
        return self.__mqtt_client
