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
import ssl
from typing import List

import paho.mqtt.client as paho

from deye_config import DeyeConfig
from deye_observation import Observation

import time


class DeyeMqttPublishError(Exception):
    def __init__(self, message: str):
        self.message = message


class DeyeMqttClient:
    def __init__(self, config: DeyeConfig):
        self.__log = logging.getLogger(DeyeMqttClient.__name__)
        self.__mqtt_client = paho.Client(
            client_id=f"deye-inverter-{config.logger.serial_number}", reconnect_on_failure=True, clean_session=True
        )
        self.__mqtt_client.enable_logger()
        if config.mqtt.tls.enabled:
            if config.mqtt.tls.insecure:
                self.__mqtt_client.tls_set(cert_reqs=ssl.CERT_NONE)
                self.__mqtt_client.tls_insecure_set(True)
                self.__log.info(
                    "Enabled TLS encryption for MQTT Broker connection without certificate verification (insecure)"
                )
            else:
                self.__mqtt_client.tls_set(
                    ca_certs=config.mqtt.tls.ca_cert_path,
                    certfile=config.mqtt.tls.client_cert_path,
                    keyfile=config.mqtt.tls.client_key_path,
                )
                self.__log.info("Enabled TLS encryption for MQTT Broker connection with certificate verification")
        if config.mqtt.username and config.mqtt.password:
            self.__mqtt_client.username_pw_set(username=config.mqtt.username, password=config.mqtt.password)
        self.__status_topic = f"{config.mqtt.topic_prefix}/{config.mqtt.availability_topic}"
        self.__mqtt_client.will_set(self.__status_topic, "offline", retain=True, qos=1)
        self.__config = config.mqtt
        self.__mqtt_timeout = 3  # seconds

    def subscribe(self, topic: str, callback):
        self.__log.info("Subscribing to topic: %s", topic)
        result, mid = self.__mqtt_client.subscribe(topic, qos=1)
        if result != paho.MQTT_ERR_SUCCESS:
            self.__log.error("Failed to subscribe to topic %s", topic)
            return
        self.__mqtt_client.message_callback_add(topic, callback)

    def connect(self) -> bool:
        if self.__mqtt_client.is_connected():
            return True
        try:
            self.__mqtt_client.connect(self.__config.host, self.__config.port, keepalive=60)
            self.__mqtt_client.loop_start()
            while not self.__mqtt_client.is_connected():
                time.sleep(1)
            self.__mqtt_client.publish(self.__status_topic, "online", retain=True, qos=1)
            self.__log.info(
                "Successfully connected to MQTT Broker located at %s:%d", self.__config.host, self.__config.port
            )
            return True
        except (ConnectionRefusedError, OSError):
            self.__log.error(
                "Failed to connect to MQTT Broker located at %s:%d", self.__config.host, self.__config.port
            )
            return False

    def disconnect(self):
        self.__mqtt_client.disconnect()

    def __do_publish(self, mqtt_topic: str, value: str):
        try:
            self.__log.debug("Publishing message. topic: '%s', value: '%s'", mqtt_topic, value)
            self.connect()
            info = self.__mqtt_client.publish(mqtt_topic, value, qos=1)
            info.wait_for_publish(self.__mqtt_timeout)
        except ValueError as e:
            raise DeyeMqttPublishError(f"MQTT outgoing queue is full: {str(e)}")
        except RuntimeError as e:
            raise DeyeMqttPublishError(f"Unknown MQTT publishing error: {str(e)}")
        except OSError as e:
            raise DeyeMqttPublishError(f"MQTT connection error: {str(e)}")

    def publish_observation(self, observation: Observation):
        if observation.sensor.mqtt_topic_suffix:
            mqtt_topic = f"{self.__config.topic_prefix}/{observation.sensor.mqtt_topic_suffix}"
            value = observation.value_as_str()
            self.__do_publish(mqtt_topic, value)

    def publish_observations(self, observations: List[Observation]):
        for observation in observations:
            if observation.sensor.mqtt_topic_suffix:
                self.publish_observation(observation)

    def publish_logger_status(self, is_online: bool):
        mqtt_topic = f"{self.__config.topic_prefix}/{self.__config.logger_status_topic}"
        value = "online" if is_online else "offline"
        self.__do_publish(mqtt_topic, value)
        self.__log.info("Logger is %s", value)

    def extract_command_topic_suffix(self, topic: str) -> str | None:
        prefix = f"{self.__config.topic_prefix}/"
        suffix = "/command"
        if topic.startswith(prefix) and topic.endswith(suffix):
            return topic.replace(prefix, "").replace(suffix, "")
        else:
            return None
