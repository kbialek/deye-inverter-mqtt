import logging
import sys
import time
import datetime

from deye_config import DeyeConfig, DeyeMqttConfig, DeyeInverterConfig
from deye_connector import DeyeConnector
from deye_modbus import DeyeModbus
from deye_sensors import sensor_list
from deye_mqtt import DeyeMqttClient
from deye_observation import Observation

config = DeyeConfig.from_env()

Log_Format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

logging.basicConfig(stream=sys.stdout, format=Log_Format, level=logging.getLevelName(config.log_level))

log = logging.getLogger('main')

mqtt_client = DeyeMqttClient(config)
connector = DeyeConnector(config)
modbus = DeyeModbus(config, connector)


def do_task():
    log.info("Reading start")
    regs = modbus.read_registers(0x3c, 0x4f) \
        | modbus.read_registers(0x50, 0x5f) \
        | modbus.read_registers(0x6d, 0x70)
    timestamp = datetime.datetime.now()
    observations = []
    for sensor in sensor_list:
        value = sensor.read_value(regs)
        if value is not None:
            observation = Observation(sensor, timestamp, value)
            observations.append(observation)
            log.debug(f'{observation.sensor.name}: {observation.value_as_str()}')

    mqtt_client.publish_observations(observations)
    log.info("Reading completed")

while True:
    do_task()
    time.sleep(10)
