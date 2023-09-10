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
import ssl

LOG_DEST_STDOUT = "STDOUT"
LOG_DEST_STDERR = "STDERR"


class DeyeMqttTlsConfig:
    def __init__(
        self,
        enabled: bool = False,
        ca_cert_path: str | None = None,
        client_cert_path: str | None = None,
        client_key_path: str | None = None,
        tls_version=ssl.PROTOCOL_TLSv1_2,
        insecure=False,
    ):
        self.enabled = enabled
        self.ca_cert_path = ca_cert_path
        self.client_cert_path = client_cert_path
        self.client_key_path = client_key_path
        ssl.TLSVersion = tls_version
        self.insecure = insecure

    @staticmethod
    def from_env():
        return DeyeMqttTlsConfig(
            enabled=os.getenv("MQTT_TLS_ENABLED", "false") == "true",
            ca_cert_path=os.getenv("MQTT_TLS_CA_CERT_PATH", None),
            client_cert_path=os.getenv("MQTT_TLS_CLIENT_CERT_PATH", None),
            client_key_path=os.getenv("MQTT_TLS_CLIENT_KEY_PATH", None),
            insecure=os.getenv("MQTT_TLS_INSECURE", "false") == "true",
        )


class DeyeMqttConfig:
    def __init__(
        self,
        host: str,
        port: int,
        username: str | None,
        password: str | None,
        topic_prefix: str,
        availability_topic: str = "status",
        logger_status_topic: str = "logger_status",
        tls=DeyeMqttTlsConfig(),
    ):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.topic_prefix = topic_prefix
        self.availability_topic = availability_topic
        self.logger_status_topic = logger_status_topic
        self.tls = tls

    @staticmethod
    def from_env():
        return DeyeMqttConfig(
            host=os.getenv("MQTT_HOST"),
            port=int(os.getenv("MQTT_PORT", "1883")),
            username=os.getenv("MQTT_USERNAME"),
            password=os.getenv("MQTT_PASSWORD"),
            topic_prefix=os.getenv("MQTT_TOPIC_PREFIX", "deye"),
            availability_topic=os.getenv("MQTT_AVAILABILITY_TOPIC", "status"),
            logger_status_topic=os.getenv("MQTT_LOGGER_STATUS_TOPIC", "logger_status"),
            tls=DeyeMqttTlsConfig.from_env(),
        )


class DeyeLoggerConfig:
    """
    Logger is a device that connects the Solar Inverter with the internet.

    Logger is identified by a unique serial number. It is required when communicating
    with the device.
    """

    def __init__(self, serial_number: int, ip_address: str, port: int, protocol: str = "tcp"):
        self.serial_number = serial_number
        self.ip_address = ip_address
        if protocol not in ["tcp", "at"]:
            raise Exception(f"Unsupported protocol {protocol}")
        self.protocol = protocol
        if port == 0 and protocol == "tcp":
            self.port = 8899
        elif port == 0 and protocol == "at":
            self.port = 48899
        else:
            self.port = port

    @staticmethod
    def from_env():
        return DeyeLoggerConfig(
            serial_number=int(os.getenv("DEYE_LOGGER_SERIAL_NUMBER")),
            ip_address=os.getenv("DEYE_LOGGER_IP_ADDRESS"),
            port=int(os.getenv("DEYE_LOGGER_PORT", "0")),
            protocol=os.getenv("DEYE_LOGGER_PROTOCOL", "tcp"),
        )


class DeyeConfig:
    def __init__(
        self,
        logger_config: DeyeLoggerConfig,
        mqtt: DeyeMqttConfig,
        log_level="INFO",
        log_stream=LOG_DEST_STDOUT,
        data_read_inverval=60,
        publish_on_change=False,
        event_expiry=360,
        metric_groups: [str] = [],
        active_processors: [str] = [],
        active_command_handlers: [str] = [],
        plugins_dir: str = "",
    ):
        self.logger = logger_config
        self.mqtt = mqtt
        self.log_level = log_level
        self.log_stream = log_stream
        self.data_read_inverval = data_read_inverval
        self.publish_on_change = publish_on_change
        self.event_expiry = event_expiry
        self.metric_groups = metric_groups
        self.active_processors = active_processors
        self.active_command_handlers = active_command_handlers
        self.plugins_dir = plugins_dir

    @staticmethod
    def from_env():
        return DeyeConfig(
            DeyeLoggerConfig.from_env(),
            DeyeMqttConfig.from_env(),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            log_stream=os.getenv("LOG_STREAM", LOG_DEST_STDOUT),
            data_read_inverval=int(os.getenv("DEYE_DATA_READ_INTERVAL", "60")),
            publish_on_change=os.getenv("DEYE_PUBLISH_ON_CHANGE", "false") == "true",
            event_expiry=int(os.getenv("DEYE_PUBLISH_ON_CHANGE_MAX_INTERVAL", 360)),
            metric_groups=DeyeConfig.__read_item_set(os.getenv("DEYE_METRIC_GROUPS", "")),
            active_processors=DeyeConfig.__read_active_processors(),
            active_command_handlers=DeyeConfig.__read_active_command_handlers(),
            plugins_dir=os.getenv("PLUGINS_DIR", "plugins"),
        )

    @staticmethod
    def __read_item_set(value: str) -> set[str]:
        return set([p.strip() for p in value.split(",")])

    @staticmethod
    def __read_active_processors() -> [str]:
        active_processors = []
        if os.getenv("DEYE_FEATURE_MQTT_PUBLISHER", "true") == "true":
            active_processors.append("mqtt_publisher")
        if os.getenv("DEYE_FEATURE_SET_TIME", "false") == "true":
            active_processors.append("set_time")
        return active_processors

    @staticmethod
    def __read_active_command_handlers() -> [str]:
        active_command_handlers = []
        if os.getenv("DEYE_FEATURE_ACTIVE_POWER_REGULATION", "false") == "true":
            active_command_handlers.append("active_power_regulation")
        return active_command_handlers
