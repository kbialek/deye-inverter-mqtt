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

import subprocess
import threading
import os
import time
from datetime import datetime
import paho.mqtt.client as paho
import pytest

from deye_observation import Observation
from deye_sensors import string_dc_power_sensor
from deye_mqtt import DeyeMqttClient
from deye_config import DeyeConfig, DeyeMqttConfig, DeyeLoggerConfig, DeyeMqttTlsConfig

import sys
import logging

log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(stream=sys.stdout, format=log_format, level=logging.DEBUG)


class TestDeyeMqttClient:
    mqtt_broker_port = 9883
    _broker_proc = None

    def __start_broker(self):
        self._broker_proc = subprocess.Popen(
            ["/usr/sbin/mosquitto", "-p", str(self.mqtt_broker_port)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        time.sleep(2)

    def __start_broker_with_tls(self):
        self._broker_proc = subprocess.Popen(
            ["/usr/sbin/mosquitto", "-p", str(self.mqtt_broker_port), "-c", "mosquitto/mosquitto-tls.conf"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        time.sleep(2)

    def __stop_broker(self):
        if self._broker_proc:
            self._broker_proc.kill()
            self._broker_proc.wait()
        time.sleep(5)

    def __connect_test_client(self):
        self.test_mqtt_client.connect("localhost", port=self.mqtt_broker_port)

    def __connect_test_client_with_tls(self):
        self.test_mqtt_client.tls_set(
            ca_certs="certs/ca.crt", certfile="certs/test_client.crt", keyfile="certs/test_client.key"
        )
        self.test_mqtt_client.connect("localhost", port=self.mqtt_broker_port)

    def __subscribe(self, topic: str):
        # Wait for SUBACK before returning so the subscription is active before the first publish.
        subscribed = threading.Event()
        self.test_mqtt_client.on_subscribe = lambda client, userdata, mid, granted_qos: subscribed.set()
        self.test_mqtt_client.loop_start()
        self.test_mqtt_client.subscribe(topic)
        subscribed.wait(timeout=10)

    @pytest.fixture(autouse=True)
    def setup(self):
        self.received_messages = []
        self.config = DeyeConfig(
            logger_configs=DeyeLoggerConfig("123456", "192.168.0.1", 9090),
            mqtt=DeyeMqttConfig("localhost", self.mqtt_broker_port, "", "", "deye"),
        )
        self.config_with_tls = DeyeConfig(
            logger_configs=DeyeLoggerConfig("123456", "192.168.0.1", 9090),
            mqtt=DeyeMqttConfig(
                "localhost",
                self.mqtt_broker_port,
                "",
                "",
                "deye",
                tls=DeyeMqttTlsConfig(
                    enabled=True,
                    ca_cert_path="certs/ca.crt",
                    client_cert_path="certs/deye.crt",
                    client_key_path="certs/deye.key",
                ),
            ),
        )
        self.test_mqtt_client = paho.Client("test_client")

        def on_message(client, userdata, msg):
            self.received_messages.append(msg)

        self.test_mqtt_client.on_message = on_message

        yield

        self.test_mqtt_client.disconnect()
        self.__stop_broker()

    def test_publish_message(self):
        # given
        self.__start_broker()
        self.__connect_test_client()

        # and
        mqtt = DeyeMqttClient(self.config)
        mqtt.connect()

        # and
        timestamp = datetime.now()
        observation = Observation(string_dc_power_sensor, timestamp, 1.2)

        # and
        self.__subscribe(f"deye/{string_dc_power_sensor.mqtt_topic_suffix}")

        # when
        mqtt.publish_observation(observation, 0)
        self.test_mqtt_client.loop_stop()

        # and
        mqtt.disconnect()

        # then
        assert len(self.received_messages) == 1

        # and
        received_message = self.received_messages[0]
        assert received_message.topic == "deye/dc/total_power"
        assert received_message.payload == b"1.2"

    def test_reconnect_on_broker_restart(self):
        # given
        self.__start_broker()

        # and: connect
        mqtt = DeyeMqttClient(self.config)
        mqtt.connect()

        # and: restart broker
        self.__stop_broker()
        self.__start_broker()

        # and
        timestamp = datetime.now()
        observation = Observation(string_dc_power_sensor, timestamp, 1.2)

        # and
        self.__connect_test_client()
        self.__subscribe(f"deye/{string_dc_power_sensor.mqtt_topic_suffix}")

        # when
        mqtt.publish_observation(observation, 0)
        self.test_mqtt_client.loop_stop()

        # and
        mqtt.disconnect()

        # then
        assert len(self.received_messages) == 1

        # and
        received_message = self.received_messages[0]
        assert received_message.topic == "deye/dc/total_power"
        assert received_message.payload == b"1.2"

    def test_resend_availability_status_on_reconnect(self):
        # given
        self.__start_broker()

        # and
        self.__connect_test_client()
        self.__subscribe("deye/status")

        # when: connect
        mqtt = DeyeMqttClient(self.config)
        mqtt.connect()
        time.sleep(3)

        # then
        assert len(self.received_messages) == 1

        # and
        received_message = self.received_messages[0]
        assert received_message.topic == "deye/status"
        assert received_message.payload == b"online"
        self.received_messages.clear()

        # and
        self.test_mqtt_client.loop_stop()

        # and: restart broker
        self.__stop_broker()
        self.__start_broker()

        # and: recreate a test client
        self.__connect_test_client()
        self.__subscribe("deye/status")

        # and: send an observation, so the client can reconnect
        timestamp = datetime.now()
        observation = Observation(string_dc_power_sensor, timestamp, 1.2)
        mqtt.publish_observation(observation, 0)
        # Wait for "online" to be published and delivered after reconnect.
        time.sleep(2)

        # then
        assert len(self.received_messages) == 1

        # and
        received_message = self.received_messages[0]
        assert received_message.topic == "deye/status"
        assert received_message.payload == b"online"

        # and
        self.test_mqtt_client.loop_stop()

        # and
        mqtt.disconnect()

    def test_connect_on_publish(self):
        # given: broker is stopped

        # and: connect
        mqtt = DeyeMqttClient(self.config)
        mqtt.connect()

        # and: start broker
        self.__start_broker()

        # and
        timestamp = datetime.now()
        observation = Observation(string_dc_power_sensor, timestamp, 1.2)

        # and
        self.__connect_test_client()
        self.__subscribe(f"deye/{string_dc_power_sensor.mqtt_topic_suffix}")

        # when
        mqtt.publish_observation(observation, 0)
        self.test_mqtt_client.loop_stop()

        # and
        mqtt.disconnect()

        # then
        assert len(self.received_messages) == 1

        # and
        received_message = self.received_messages[0]
        assert received_message.topic == "deye/dc/total_power"
        assert received_message.payload == b"1.2"

    def test_publish_message_with_tls(self):
        # given
        self.__start_broker_with_tls()
        self.__connect_test_client_with_tls()

        # and
        mqtt = DeyeMqttClient(self.config_with_tls)
        mqtt.connect()

        # and
        timestamp = datetime.now()
        observation = Observation(string_dc_power_sensor, timestamp, 1.2)

        # and
        self.__subscribe(f"deye/{string_dc_power_sensor.mqtt_topic_suffix}")

        # when
        mqtt.publish_observation(observation, 0)
        self.test_mqtt_client.loop_stop()

        # and
        mqtt.disconnect()

        # then
        assert len(self.received_messages) == 1

        # and
        received_message = self.received_messages[0]
        assert received_message.topic == "deye/dc/total_power"
        assert received_message.payload == b"1.2"
