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

import logging
import signal
import threading
import time

from deye_config import DeyeConfig
from deye_connector_factory import DeyeConnectorFactory
from deye_modbus import DeyeModbus
from deye_mqtt import DeyeMqttClient
from deye_sensor import SensorRegisterRanges
from deye_sensors import sensor_list, sensor_register_ranges
from deye_processor_factory import DeyeProcessorFactory
from deye_inverter_state import DeyeInverterState


class DeyeDaemon:
    def __init__(self, config: DeyeConfig):
        self.__log = logging.getLogger(DeyeDaemon.__name__)
        self.__config = config
        self.__log.info(
            "Please help me build the list of compatible inverters. "
            "https://github.com/kbialek/deye-inverter-mqtt/issues/41"
        )

        connector = DeyeConnectorFactory(config).create_connector()
        modbus = DeyeModbus(connector)
        sensors = [s for s in sensor_list if s.in_any_group(self.__config.metric_groups)]
        reg_ranges = SensorRegisterRanges(
            sensor_register_ranges, config.metric_groups, max_range_length=config.logger.max_register_range_length
        )

        mqtt_client = DeyeMqttClient(self.__config)

        processors = DeyeProcessorFactory(self.__config, mqtt_client).create_processors(modbus, sensors)
        self.__inverter_state = DeyeInverterState(config, reg_ranges, modbus, sensors, processors)
        self.__interval_runner = IntervalRunner(
            self.__config.data_read_inverval, self.__inverter_state.read_from_logger
        )

    def run(self):
        self.__interval_runner.start()


class IntervalRunner:
    def __init__(self, interval, action):
        self.__log = logging.getLogger(DeyeDaemon.__name__)
        self.__interval = interval
        self.__action = action
        self.__stopEvent = threading.Event()
        self.__thread = threading.Thread(target=self.__handler)
        self.__log.debug("Start to execute the daemon at intervals of %s seconds", self.__interval)

    def __handler(self):
        nextTime = time.time()
        while not self.__stopEvent.wait(nextTime - time.time()):
            nextTime = time.time() + self.__interval
            self.__invoke_action()

    def __invoke_action(self):
        try:
            self.__action()
        except Exception:
            self.__log.exception("Unexpected error during daemon execution")

    def start(self):
        signal.signal(signal.SIGINT, self.cancel)
        signal.signal(signal.SIGTERM, self.cancel)
        self.__thread.start()

    def cancel(self, _signum, _frame):
        self.__stopEvent.set()


def main():
    config = DeyeConfig.from_env()
    daemon = DeyeDaemon(config)
    daemon.run()


if __name__ == "__main__":
    main()
