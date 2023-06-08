import logging

from deye_config import DeyeConfig
from deye_mqtt import DeyeMqttClient
from deye_modbus import DeyeModbus

from deye_command_handlers import DeyeCommandHandler, DeyeActivePowerRegulationCommandHandler


class DeyeMqttSubscriber:
    def __init__(self, config: DeyeConfig, mqtt_client: DeyeMqttClient, modbus: DeyeModbus):
        self.__log = logging.getLogger(DeyeMqttSubscriber.__name__)
        command_handlers: [DeyeCommandHandler] = [DeyeActivePowerRegulationCommandHandler(modbus)]

        active_command_handlers = [h for h in command_handlers if h.id in config.active_command_handlers]

        if active_command_handlers:
            mqtt_client.connect()
            for command_handler in active_command_handlers:
                command_handler.initialize(config, mqtt_client)
