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

import os


class DeyeMqttConfig():
    def __init__(self, host: str, port: int, username: str, password: str, topic_prefix: str,
                 availability_topic: str = 'status',
                 logger_status_topic: str = 'logger_status'):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.topic_prefix = topic_prefix
        self.availability_topic = availability_topic
        self.logger_status_topic = logger_status_topic

    @staticmethod
    def from_env():
        return DeyeMqttConfig(
            host=os.getenv('MQTT_HOST'),
            port=int(os.getenv('MQTT_PORT')),
            username=os.getenv('MQTT_USERNAME'),
            password=os.getenv('MQTT_PASSWORD'),
            topic_prefix=os.getenv('MQTT_TOPIC_PREFIX'),
            availability_topic=os.getenv('MQTT_AVAILIBILITY_TOPIC', 'status'),
            logger_status_topic=os.getenv('MQTT_LOGGER_STATUS_TOPIC', 'logger_status')
        )


class DeyeLoggerConfig():
    """
    Logger is a device that connects the Solar Inverter with the internet.

    Logger is identified by a unique serial number. It is required when communicating
    with the device.
    """

    def __init__(self, serial_number: int, ip_address: str, port: int):
        self.serial_number = serial_number
        self.ip_address = ip_address
        self.port = port

    @staticmethod
    def from_env():
        return DeyeLoggerConfig(
            serial_number=int(os.getenv('DEYE_LOGGER_SERIAL_NUMBER')),
            ip_address=os.getenv('DEYE_LOGGER_IP_ADDRESS'),
            port=int(os.getenv('DEYE_LOGGER_PORT')),
        )


class DeyeConfig():
    def __init__(self, logger_config: DeyeLoggerConfig, mqtt: DeyeMqttConfig,
                 log_level='INFO',
                 data_read_inverval=60,
                 metric_groups=[]):
        self.logger = logger_config
        self.mqtt = mqtt
        self.log_level = log_level
        self.data_read_inverval = data_read_inverval
        self.metric_groups = metric_groups

    @staticmethod
    def from_env():
        return DeyeConfig(DeyeLoggerConfig.from_env(), DeyeMqttConfig.from_env(),
                          log_level=os.getenv('LOG_LEVEL', 'INFO'),
                          data_read_inverval=int(os.getenv('DEYE_DATA_READ_INTERVAL', '60')),
                          metric_groups=set([p.strip() for p in os.getenv('DEYE_METRIC_GROUPS', '').split(',')])
                          )
