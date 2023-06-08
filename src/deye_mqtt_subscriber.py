import logging

from deye_config import DeyeConfig
from deye_mqtt import DeyeMqttClient
from deye_modbus import DeyeModbus
from paho.mqtt.client import Client, MQTTMessage


class DeyeMqttSubscriber:
    def __init__(self, config: DeyeConfig, mqtt_client: DeyeMqttClient, modbus: DeyeModbus):
        self.__log = logging.getLogger(DeyeMqttSubscriber.__name__)
        self.__modbus = modbus
        mqtt_client.subscribe(
            f"{config.mqtt.topic_prefix}/settings/active_power_regulation", self.__on_active_power_regulation
        )

    def get_id(self):
        return "active_power_regulation"

    def __on_active_power_regulation(self, client: Client, userdata, msg: MQTTMessage):
        try:
            active_power_regulation_factor = float(msg.payload)
        except ValueError:
            self.__log.error("Invalid active power regulation value: %s", msg.payload)
            return

        if active_power_regulation_factor > 120:
            self.__log.error("Given active power regulation value is too high: %f", active_power_regulation_factor)
            return

        if active_power_regulation_factor < 0:
            self.__log.error("Given active power regulation value is too low: %f", active_power_regulation_factor)
            return

        self.__log.info("Setting active power regulation to %f", active_power_regulation_factor)
        self.__modbus.write_register(40, int(active_power_regulation_factor * 10))
