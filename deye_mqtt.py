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

from typing import List
import logging

import paho.mqtt.client as paho

from deye_config import DeyeConfig
from deye_observation import Observation


class DeyeMqttClient():

    def __init__(self, config: DeyeConfig):
        self.__log = logging.getLogger(DeyeMqttClient.__name__)
        self.__mqtt_client = paho.Client("deye_inverter")
        self.__mqtt_client.username_pw_set(username=config.mqtt.username, password=config.mqtt.password)
        self.__config = config.mqtt

    def publish_observation(self, observation: Observation):
        self.__mqtt_client.connect(self.__config.host, self.__config.port)
        if observation.sensor.mqtt_topic_suffix:
            mqtt_topic = f'{self.__config.topic_prefix}/{observation.sensor.mqtt_topic_suffix}'
            self.__mqtt_client.publish(mqtt_topic, observation.value_as_str())
        self.__mqtt_client.disconnect()

    def publish_observations(self, observations: List[Observation]):
        try:
            self.__mqtt_client.connect(self.__config.host, self.__config.port)
            for observation in observations:
                if observation.sensor.mqtt_topic_suffix:
                    mqtt_topic = f'{self.__config.topic_prefix}/{observation.sensor.mqtt_topic_suffix}'
                    self.__mqtt_client.publish(mqtt_topic, observation.value_as_str())
            self.__mqtt_client.disconnect()
        except OSError as e:
            self.__log.error("MQTT connection error %s", str(e))