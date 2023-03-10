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

from datetime import datetime

from deye_events import DeyeEvent, DeyeEventProcessor, DeyeLoggerStatusEvent
from deye_modbus import DeyeModbus


class DeyeSetTimeProcessor(DeyeEventProcessor):
    """
    Set logger time when the logger becomes available online.
    """

    def __init__(self, modbus: DeyeModbus):
        self.__log = logging.getLogger(DeyeSetTimeProcessor.__name__)
        self.__modbus = modbus
        self.__last_status = False

    def process(self, events: list[DeyeEvent]):
        logger_status_events: list[DeyeLoggerStatusEvent] = [
            event for event in events if isinstance(event, DeyeLoggerStatusEvent)
        ]
        if logger_status_events:
            logger_status = logger_status_events[0].online
            if not self.__last_status and logger_status:
                self.__set_time()
            self.__last_status = logger_status

    def __set_time(self):
        now = datetime.now()
        # year and month
        self.__modbus.write_register(22, 256 * now.month + now.year)
        # day and hour
        self.__modbus.write_register(23, 256 * now.hour + now.day)
        # minute and seconds
        self.__modbus.write_register(24, 256 * now.second + now.minute)
        self.__log.info(f'Logger time set to {now}')
