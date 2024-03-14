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

from deye_sensor import SingleRegisterSensor, SensorRegisterRange

deye_settings_active_power_regulation_default = SingleRegisterSensor(
    "Active power regulation",
    40,
    0.1,
    mqtt_topic_suffix="settings/active_power_regulation",
    unit="%",
    signed=False,
    groups=["settings"],
)

deye_settings_active_power_regulation_micro = SingleRegisterSensor(
    "Active power regulation",
    40,
    1,
    mqtt_topic_suffix="settings/active_power_regulation",
    unit="%",
    signed=False,
    groups=["settings_micro"],
)

deye_settings_sensors = [deye_settings_active_power_regulation_default, deye_settings_active_power_regulation_micro]

deye_settings_register_ranges = [
    SensorRegisterRange(group={"settings", "settings_micro"}, first_reg_address=40, last_reg_address=40),
]
