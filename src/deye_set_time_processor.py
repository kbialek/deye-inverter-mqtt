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

from deye_events import DeyeEventList, DeyeEventProcessor
from deye_modbus import DeyeModbus


class DeyeSetTimeProcessor(DeyeEventProcessor):
    """
    Set logger time when the logger becomes available online.
    """

    def __init__(self, modbus: DeyeModbus):
        self.__log = logging.getLogger(DeyeSetTimeProcessor.__name__)
        self.__modbus = modbus
        self.__last_status = False

    def get_id(self):
        return "set_time"

    @property
    def last_status(self):
        return self.__last_status

    def process(self, events: DeyeEventList):
        logger_status = events.get_status()
        if logger_status is not None:
            if not self.__last_status and logger_status:
                self.__last_status = self.__set_time()
            else:
                self.__last_status = logger_status

    def __set_time(self) -> bool:
        now = datetime.now()
        write_status = self.__modbus.write_registers(
            22,
            [
                # year and month
                256 * (now.year % 100) + now.month,
                # day and hour
                256 * now.day + now.hour,
                # minute and seconds
                256 * now.minute + now.second,
            ],
        )
        if write_status:
            self.__log.info(f"Logger time set to {now}")
        else:
            self.__log.warning("Failed to set logger time")
        return write_status
