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

import unittest
import os
import time
from unittest.mock import patch
from datetime import datetime
import paho.mqtt.client as paho

from deye_observation import Observation
from deye_sensors import string_dc_power_sensor
from deye_mqtt import DeyeMqttClient
from deye_config import DeyeConfig, DeyeMqttConfig

import sys
import logging

log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(stream=sys.stdout, format=log_format, level=logging.DEBUG)

class DeyeMqttClientIntegrationTest(unittest.TestCase):

    def setUp(self):
        mqtt_broker_port = 9883
        self.config = DeyeConfig(
            logger_config=None,
            mqtt=DeyeMqttConfig('localhost', mqtt_broker_port, '', '', 'deye')
        )
        self.mosquitto_pid = os.spawnl(os.P_NOWAIT, '/usr/sbin/mosquitto',
                                       '/usr/sbin/mosquitto', '-p', str(mqtt_broker_port))
        time.sleep(2)
        self.test_mqtt_client = paho.Client("test_client")
        self.test_mqtt_client.connect('localhost', port=mqtt_broker_port)
        self.received_messages = []

        def on_message(client, userdata, msg):
            self.received_messages.append(msg)
        self.test_mqtt_client.on_message = on_message

    def tearDown(self):
        self.test_mqtt_client.disconnect()
        os.kill(self.mosquitto_pid, 9)

    def test_publish_message(self):
        # given
        mqtt = DeyeMqttClient(self.config)

        # and
        timestamp = datetime.now()
        observation = Observation(string_dc_power_sensor, timestamp, 1.2)

        # and
        self.test_mqtt_client.subscribe(f'deye/{string_dc_power_sensor.mqtt_topic_suffix}')

        # when
        self.test_mqtt_client.loop_start()
        mqtt.publish_observation(observation)
        self.test_mqtt_client.loop_stop()

        # then
        self.assertEqual(len(self.received_messages), 1)
        
        # and
        received_message = self.received_messages[0]
        self.assertEqual(received_message.topic, 'deye/dc/total_power')
        self.assertEqual(received_message.payload, b'1.2')

if __name__ == '__main__':
    unittest.main()
