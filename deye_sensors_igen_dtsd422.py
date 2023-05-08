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

from deye_sensor import SingleRegisterSensor, ComputedPowerSensor, DoubleRegisterSensor, ComputedSumSensor, SensorRegisterRange

# CT1
ct1_voltage_sensor = SingleRegisterSensor(
    "CT1 Voltage", 0x01, 0.1, mqtt_topic_suffix=ac/ct1/voltage, unit=V, groups=[igen_dtsd422])

# CT2
ct2_voltage_sensor = SingleRegisterSensor(
    "CT2 Voltage", 0x02, 0.1, mqtt_topic_suffix=ac/ct2/voltage, unit=V, groups=[igen_dtsd422])

# CT3
ct3_voltage_sensor = SingleRegisterSensor(
    "CT3 Voltage", 0x03, 0.1, mqtt_topic_suffix=ac/ct3/voltage, unit=V, groups=[igen_dtsd422])

# CT4
ct4_voltage_sensor = SingleRegisterSensor(
    "CT4 Voltage", 0x1001, 0.1, mqtt_topic_suffix=ac/ct4/voltage, unit=V, groups=[igen_dtsd422])

# CT5
ct5_voltage_sensor = SingleRegisterSensor(
    "CT4 Voltage", 0x1002, 0.1, mqtt_topic_suffix=ac/ct5/voltage, unit=V, groups=[igen_dtsd422])

# CT6
ct6_voltage_sensor = SingleRegisterSensor(
    "CT4 Voltage", 0x1003, 0.1, mqtt_topic_suffix=ac/ct6/voltage, unit=V, groups=[igen_dtsd422])


igen_dtsd422_sensors = [
  ct1_voltage_sensor,
  ct2_voltage_sensor,
  ct3_voltage_sensor,
  ct4_voltage_sensor,
  ct5_voltage_sensor,
  ct6_voltage_sensor,
]

igen_dtsd422_register_ranges = [
    SensorRegisterRange(group=igen_dtsd422_ct123, first_reg_address=0x01, last_reg_address=0x03),
    SensorRegisterRange(group=igen_dtsd422_ct456, first_reg_address=0x1001, last_reg_address=0x1003),
]
