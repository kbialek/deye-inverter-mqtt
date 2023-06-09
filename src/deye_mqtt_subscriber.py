import logging

from deye_config import DeyeConfig
from deye_mqtt import DeyeMqttClient
from deye_modbus import DeyeModbus

from deye_command_handlers import DeyeCommandHandler, DeyeActivePowerRegulationCommandHandler


class DeyeMqttSubscriber:
    @staticmethod
    def create(config: DeyeConfig, mqtt_client: DeyeMqttClient, modbus: DeyeModbus) -> "DeyeMqttSubscriber":
        command_handlers = [DeyeActivePowerRegulationCommandHandler(modbus)]
        return DeyeMqttSubscriber(config, mqtt_client, modbus, command_handlers)

    def __init__(
        self,
        config: DeyeConfig,
        mqtt_client: DeyeMqttClient,
        modbus: DeyeModbus,
        command_handlers: [DeyeCommandHandler],
    ):
        self.__log = logging.getLogger(DeyeMqttSubscriber.__name__)

        active_command_handlers = [h for h in command_handlers if h.id in config.active_command_handlers]

        if active_command_handlers:
            mqtt_client.connect()
            for command_handler in active_command_handlers:
                command_handler.initialize(config, mqtt_client)
