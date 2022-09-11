import os


class DeyeMqttConfig():
    def __init__(self, host: str, port: int, username: str, password: str, topic_prefix: str):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.topic_prefix = topic_prefix

    @staticmethod
    def from_env():
        return DeyeMqttConfig(
            host=os.getenv('DEYE_MQTT_HOST'),
            port=int(os.getenv('DEYE_MQTT_PORT')),
            username=os.getenv('DEYE_MQTT_USERNAME'),
            password=os.getenv('DEYE_MQTT_PASSWORD'),
            topic_prefix=os.getenv('DEYE_MQTT_TOPIC_PREFIX')
        )


class DeyeInverterConfig():
    def __init__(self, serial_number: int, ip_address: str, port: int):
        self.serial_number = serial_number
        self.ip_address = ip_address
        self.port = port

    @staticmethod
    def from_env():
        return DeyeInverterConfig(
            serial_number=int(os.getenv('DEYE_INVERTER_SERIAL_NUMBER')),
            ip_address=os.getenv('DEYE_INVERTER_IP_ADDRESS'),
            port=int(os.getenv('DEYE_INVERTER_PORT')),
        )


class DeyeConfig():
    def __init__(self, inverter: DeyeInverterConfig, mqtt: DeyeMqttConfig,
        log_level = 'INFO',
        data_read_inverval = 60):
        self.inverter = inverter
        self.mqtt = mqtt
        self.log_level = log_level
        self.data_read_inverval = data_read_inverval

    @staticmethod
    def from_env():
        return DeyeConfig(DeyeInverterConfig.from_env(), DeyeMqttConfig.from_env(),
            log_level=os.getenv('DEYE_LOG_LEVEL', 'INFO'),
            data_read_inverval=int(os.getenv('DEYE_DATA_READ_INTERVAL', '60'))
        )