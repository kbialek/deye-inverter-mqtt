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

from deye_sensor import Sensor
from datetime import datetime


class Observation:
    """
    Models Solar Inverter sensor reading.
    """

    def __init__(self, sensor: Sensor, timestamp: datetime, value):
        self.sensor = sensor
        self.timestamp = timestamp
        self.value = value

    def value_as_str(self):
        return self.sensor.format_value(self.value)

    def __repr__(self) -> str:
        return f"{self.sensor.mqtt_topic_suffix}@{self.timestamp}:{self.value}"
