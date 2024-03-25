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
import random

from deye_config import DeyeConfig, DeyeLoggerConfig
from deye_connector_factory import DeyeConnectorFactory
from deye_modbus import DeyeModbus
from deye_mqtt import DeyeMqttClient
from deye_sensor import SensorRegisterRanges
from deye_sensors import sensor_list, sensor_register_ranges
from deye_processor_factory import DeyeProcessorFactory
from deye_inverter_state import DeyeInverterState


class IntervalRunner:
    def __init__(self, logger_config: DeyeLoggerConfig, interval: int, action):
        self.__log = logger_config.logger_adapter(logging.getLogger(DeyeDaemon.__name__))
        self.__interval = interval
        self.__action = action
        self.__stopEvent = threading.Event()
        self.__thread = threading.Thread(target=self.__handler)

    def __handler(self):
        self.__log.debug("Start to execute the daemon at intervals of %s seconds", self.__interval)
        nextTime = time.time() + random.randint(0, self.__interval - 1)
        while not self.__stopEvent.wait(nextTime - time.time()):
            nextTime = time.time() + self.__interval
            self.__invoke_action()

    def __invoke_action(self):
        try:
            self.__action()
        except Exception:
            self.__log.exception("Unexpected error during daemon execution")

    def start(self):
        self.__thread.start()

    def stop(self):
        self.__stopEvent.set()


class DeyeDaemon:
    def __init__(self, config: DeyeConfig):
        self.__log = logging.getLogger(DeyeDaemon.__name__)
        self.__config = config
        self.__log.info(
            "Please help me build the list of compatible inverters. "
            "https://github.com/kbialek/deye-inverter-mqtt/issues/41"
        )

        self.__mqtt_client = DeyeMqttClient(self.__config)
        self.__processor_factory = DeyeProcessorFactory(self.__config, self.__mqtt_client)
        self.__interval_runners = [
            self.__create_interval_runner_for_logger(logger_config) for logger_config in config.logger_configs
        ]

    def __create_interval_runner_for_logger(self, logger_config: DeyeLoggerConfig) -> IntervalRunner:
        modbus = DeyeModbus(DeyeConnectorFactory().create_connector(logger_config))
        sensors = [s for s in sensor_list if s.in_any_group(self.__config.metric_groups)]
        reg_ranges = SensorRegisterRanges(
            sensor_register_ranges,
            self.__config.metric_groups,
            max_range_length=logger_config.max_register_range_length,
        )

        processors = self.__processor_factory.create_processors(logger_config, modbus, sensors)
        inverter_state = DeyeInverterState(self.__config, logger_config, reg_ranges, modbus, sensors, processors)
        return IntervalRunner(logger_config, self.__config.data_read_inverval, inverter_state.read_from_logger)

    def start(self):
        for interval_runner in self.__interval_runners:
            interval_runner.start()

    def stop(self, _signum, _frame):
        for interval_runner in self.__interval_runners:
            interval_runner.stop()


def main():
    config = DeyeConfig.from_env()
    daemon = DeyeDaemon(config)
    signal.signal(signal.SIGINT, daemon.stop)
    signal.signal(signal.SIGTERM, daemon.stop)
    daemon.start()


if __name__ == "__main__":
    main()
