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