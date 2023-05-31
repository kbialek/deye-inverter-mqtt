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

from deye_sensor import (
    SingleRegisterSensor,
    SignedMagnitudeSingleRegisterSensor,
    SignedMagnitudeDoubleRegisterSensor,
    SensorRegisterRange,
)

#
# IGEN DTSD-422-D3 support.
#
# Todo:
# * Daily Values for Positive and Negative energy are missing, can't find them.
# * Need to verify data is still read correctly when double reg values exceed one
#   register
#

# CT1
ct1_voltage_sensor = SingleRegisterSensor(
    "Voltage CT1",
    0x01,
    0.1,
    mqtt_topic_suffix="ct1/voltage",
    unit="V",
    groups=["igen_dtsd422"],
)
ct1_current_sensor = SignedMagnitudeDoubleRegisterSensor(
    "Current CT1",
    0x07,
    0.001,
    mqtt_topic_suffix="ct1/current",
    unit="A",
    groups=["igen_dtsd422"],
    print_format="{:0.2f}",
)
ct1_active_power_sensor = SignedMagnitudeDoubleRegisterSensor(
    "Active Power CT1",
    0x0F,
    1,
    mqtt_topic_suffix="ct1/active_power",
    unit="W",
    groups=["igen_dtsd422"],
)
ct1_reactive_power_sensor = SignedMagnitudeDoubleRegisterSensor(
    "Reactive Power CT1",
    0x17,
    1,
    mqtt_topic_suffix="ct1/reactive_power",
    unit="Var",
    groups=["igen_dtsd422"],
)
ct1_apparent_power_sensor = SignedMagnitudeDoubleRegisterSensor(
    "Apparent Power CT1",
    0x1F,
    1,
    mqtt_topic_suffix="ct1/apparent_power",
    unit="VA",
    groups=["igen_dtsd422"],
)
ct1_power_factor_sensor = SignedMagnitudeSingleRegisterSensor(
    "Power Factor CT1",
    0x26,
    0.001,
    mqtt_topic_suffix="ct1/power_factor",
    groups=["igen_dtsd422"],
)
ct1_total_positive_energy = SingleRegisterSensor(
    "Total Positive Energy CT1",
    0x3F,
    0.01,
    mqtt_topic_suffix="ct1/total_positive_energy",
    unit="kWh",
    groups=["igen_dtsd422"],
    print_format="{:0.2f}",
)
ct1_total_negative_energy = SingleRegisterSensor(
    "Total Negative Energy CT1",
    0x49,
    0.01,
    mqtt_topic_suffix="ct1/total_negative_energy",
    unit="kWh",
    groups=["igen_dtsd422"],
    print_format="{:0.2f}",
)

# CT2
ct2_voltage_sensor = SingleRegisterSensor(
    "Voltage CT2",
    0x02,
    0.1,
    mqtt_topic_suffix="ct2/voltage",
    unit="V",
    groups=["igen_dtsd422"],
)
ct2_current_sensor = SignedMagnitudeDoubleRegisterSensor(
    "Current CT2",
    0x09,
    0.001,
    mqtt_topic_suffix="ct2/current",
    unit="A",
    groups=["igen_dtsd422"],
    print_format="{:0.2f}",
)
ct2_active_power_sensor = SignedMagnitudeDoubleRegisterSensor(
    "Active Power CT2",
    0x11,
    1,
    mqtt_topic_suffix="ct2/active_power",
    unit="W",
    groups=["igen_dtsd422"],
)
ct2_reactive_power_sensor = SignedMagnitudeDoubleRegisterSensor(
    "Reactive Power CT2",
    0x19,
    1,
    mqtt_topic_suffix="ct2/reactive_power",
    unit="Var",
    groups=["igen_dtsd422"],
)
ct2_apparent_power_sensor = SignedMagnitudeDoubleRegisterSensor(
    "Apparent Power CT2",
    0x21,
    1,
    mqtt_topic_suffix="ct2/apparent_power",
    unit="VA",
    groups=["igen_dtsd422"],
)
ct2_power_factor_sensor = SignedMagnitudeSingleRegisterSensor(
    "Power Factor CT2",
    0x27,
    0.001,
    mqtt_topic_suffix="ct2/power_factor",
    groups=["igen_dtsd422"],
)
ct2_total_positive_energy = SingleRegisterSensor(
    "Total Positive Energy CT2",
    0x53,
    0.01,
    mqtt_topic_suffix="ct2/total_positive_energy",
    unit="kWh",
    groups=["igen_dtsd422"],
    print_format="{:0.2f}",
)
ct2_total_negative_energy = SingleRegisterSensor(
    "Total Negative Energy CT2",
    0x5D,
    0.01,
    mqtt_topic_suffix="ct2/total_negative_energy",
    unit="kWh",
    groups=["igen_dtsd422"],
    print_format="{:0.2f}",
)

# CT3
ct3_voltage_sensor = SingleRegisterSensor(
    "Voltage CT3",
    0x03,
    0.1,
    mqtt_topic_suffix="ct3/voltage",
    unit="V",
    groups=["igen_dtsd422"],
)
ct3_current_sensor = SignedMagnitudeDoubleRegisterSensor(
    "Current CT3",
    0x0B,
    0.001,
    mqtt_topic_suffix="ct3/current",
    unit="A",
    groups=["igen_dtsd422"],
    print_format="{:0.2f}",
)
ct3_active_power_sensor = SignedMagnitudeDoubleRegisterSensor(
    "Active Power CT3",
    0x13,
    1,
    mqtt_topic_suffix="ct3/active_power",
    unit="W",
    groups=["igen_dtsd422"],
)
ct3_reactive_power_sensor = SignedMagnitudeDoubleRegisterSensor(
    "Reactive Power CT3",
    0x1B,
    1,
    mqtt_topic_suffix="ct3/reactive_power",
    unit="Var",
    groups=["igen_dtsd422"],
)
ct3_apparent_power_sensor = SignedMagnitudeDoubleRegisterSensor(
    "Apparent Power CT3",
    0x23,
    1,
    mqtt_topic_suffix="ct3/apparent_power",
    unit="VA",
    groups=["igen_dtsd422"],
)
ct3_power_factor_sensor = SignedMagnitudeSingleRegisterSensor(
    "Power Factor CT3",
    0x28,
    0.001,
    mqtt_topic_suffix="ct3/power_factor",
    groups=["igen_dtsd422"],
)
ct3_total_positive_energy = SingleRegisterSensor(
    "Total Positive Energy CT3",
    0x67,
    0.01,
    mqtt_topic_suffix="ct3/total_positive_energy",
    unit="kWh",
    groups=["igen_dtsd422"],
    print_format="{:0.2f}",
)
ct3_total_negative_energy = SingleRegisterSensor(
    "Total Negative Energy CT3",
    0x71,
    0.01,
    mqtt_topic_suffix="ct3/total_negative_energy",
    unit="kWh",
    groups=["igen_dtsd422"],
    print_format="{:0.2f}",
)

# CT4
ct4_voltage_sensor = SingleRegisterSensor(
    "Voltage CT4",
    0x1001,
    0.1,
    mqtt_topic_suffix="ct4/voltage",
    unit="V",
    groups=["igen_dtsd422"],
)
ct4_current_sensor = SignedMagnitudeDoubleRegisterSensor(
    "Current CT4",
    0x1007,
    0.001,
    mqtt_topic_suffix="ct4/current",
    unit="A",
    groups=["igen_dtsd422"],
    print_format="{:0.2f}",
)
ct4_active_power_sensor = SignedMagnitudeDoubleRegisterSensor(
    "Active Power CT4",
    0x100F,
    1,
    mqtt_topic_suffix="ct4/active_power",
    unit="W",
    groups=["igen_dtsd422"],
)
ct4_reactive_power_sensor = SignedMagnitudeDoubleRegisterSensor(
    "Reactive Power CT4",
    0x1017,
    1,
    mqtt_topic_suffix="ct4/reactive_power",
    unit="Var",
    groups=["igen_dtsd422"],
)
ct4_apparent_power_sensor = SignedMagnitudeDoubleRegisterSensor(
    "Apparent Power CT4",
    0x101F,
    1,
    mqtt_topic_suffix="ct4/apparent_power",
    unit="VA",
    groups=["igen_dtsd422"],
)
ct4_power_factor_sensor = SignedMagnitudeSingleRegisterSensor(
    "Power Factor CT4",
    0x1026,
    0.001,
    mqtt_topic_suffix="ct4/power_factor",
    groups=["igen_dtsd422"],
)
ct4_total_positive_energy = SingleRegisterSensor(
    "Total Positive Energy CT4",
    0x103F,
    0.01,
    mqtt_topic_suffix="ct4/total_positive_energy",
    unit="kWh",
    groups=["igen_dtsd422"],
    print_format="{:0.2f}",
)
ct4_total_negative_energy = SingleRegisterSensor(
    "Total Negative Energy CT4",
    0x1049,
    0.01,
    mqtt_topic_suffix="ct4/total_negative_energy",
    unit="kWh",
    groups=["igen_dtsd422"],
    print_format="{:0.2f}",
)

# CT5
ct5_voltage_sensor = SingleRegisterSensor(
    "Voltage CT5",
    0x1002,
    0.1,
    mqtt_topic_suffix="ct5/voltage",
    unit="V",
    groups=["igen_dtsd422"],
)
ct5_current_sensor = SignedMagnitudeDoubleRegisterSensor(
    "Current CT5",
    0x1009,
    0.001,
    mqtt_topic_suffix="ct5/current",
    unit="A",
    groups=["igen_dtsd422"],
    print_format="{:0.2f}",
)
ct5_active_power_sensor = SignedMagnitudeDoubleRegisterSensor(
    "Active Power CT5",
    0x1011,
    1,
    mqtt_topic_suffix="ct5/active_power",
    unit="W",
    groups=["igen_dtsd422"],
)
ct5_reactive_power_sensor = SignedMagnitudeDoubleRegisterSensor(
    "Reactive Power CT5",
    0x1019,
    1,
    mqtt_topic_suffix="ct5/reactive_power",
    unit="Var",
    groups=["igen_dtsd422"],
)
ct5_apparent_power_sensor = SignedMagnitudeDoubleRegisterSensor(
    "Apparent Power CT5",
    0x1021,
    1,
    mqtt_topic_suffix="ct5/apparent_power",
    unit="VA",
    groups=["igen_dtsd422"],
)
ct5_power_factor_sensor = SignedMagnitudeSingleRegisterSensor(
    "Power Factor CT5",
    0x1027,
    0.001,
    mqtt_topic_suffix="ct5/power_factor",
    groups=["igen_dtsd422"],
)
ct5_total_positive_energy = SingleRegisterSensor(
    "Total Positive Energy CT5",
    0x1053,
    0.01,
    mqtt_topic_suffix="ct5/total_positive_energy",
    unit="kWh",
    groups=["igen_dtsd422"],
    print_format="{:0.2f}",
)
ct5_total_negative_energy = SingleRegisterSensor(
    "Total Negative Energy CT5",
    0x105D,
    0.01,
    mqtt_topic_suffix="ct5/total_negative_energy",
    unit="kWh",
    groups=["igen_dtsd422"],
    print_format="{:0.2f}",
)

# CT6
ct6_voltage_sensor = SingleRegisterSensor(
    "Voltage CT6",
    0x1003,
    0.1,
    mqtt_topic_suffix="ct6/voltage",
    unit="V",
    groups=["igen_dtsd422"],
)
ct6_current_sensor = SignedMagnitudeDoubleRegisterSensor(
    "Current CT6",
    0x100B,
    0.001,
    mqtt_topic_suffix="ct6/current",
    unit="A",
    groups=["igen_dtsd422"],
    print_format="{:0.2f}",
)
ct6_active_power_sensor = SignedMagnitudeDoubleRegisterSensor(
    "Active Power CT6",
    0x1013,
    1,
    mqtt_topic_suffix="ct6/active_power",
    unit="W",
    groups=["igen_dtsd422"],
)
ct6_reactive_power_sensor = SignedMagnitudeDoubleRegisterSensor(
    "Reactive Power CT6",
    0x101B,
    1,
    mqtt_topic_suffix="ct6/reactive_power",
    unit="Var",
    groups=["igen_dtsd422"],
)
ct6_apparent_power_sensor = SignedMagnitudeDoubleRegisterSensor(
    "Apparent Power CT6",
    0x1023,
    1,
    mqtt_topic_suffix="ct6/apparent_power",
    unit="VA",
    groups=["igen_dtsd422"],
)
ct6_power_factor_sensor = SignedMagnitudeSingleRegisterSensor(
    "Power Factor CT6",
    0x1028,
    0.001,
    mqtt_topic_suffix="ct6/power_factor",
    groups=["igen_dtsd422"],
)
ct6_total_positive_energy = SingleRegisterSensor(
    "Total Positive Energy CT6",
    0x1067,
    0.01,
    mqtt_topic_suffix="ct6/total_positive_energy",
    unit="kWh",
    groups=["igen_dtsd422"],
    print_format="{:0.2f}",
)
ct6_total_negative_energy = SingleRegisterSensor(
    "Total Negative Energy CT6",
    0x1071,
    0.01,
    mqtt_topic_suffix="ct6/total_negative_energy",
    unit="kWh",
    groups=["igen_dtsd422"],
    print_format="{:0.2f}",
)

# Total
total_active_power_sensor = SignedMagnitudeDoubleRegisterSensor(
    "Total Active Power",
    0x0D,
    1,
    mqtt_topic_suffix="total/active_power",
    unit="W",
    groups=["igen_dtsd422"],
)
total_active_power2_sensor = SignedMagnitudeDoubleRegisterSensor(
    "Total Active Power 2",
    0x100D,
    1,
    mqtt_topic_suffix="total/active_power2",
    unit="W",
    groups=["igen_dtsd422"],
)
total_reactive_power_sensor = SignedMagnitudeDoubleRegisterSensor(
    "Total Reactive Power",
    0x15,
    1,
    mqtt_topic_suffix="total/reactive_power",
    unit="Var",
    groups=["igen_dtsd422"],
)
total_reactive_power2_sensor = SignedMagnitudeDoubleRegisterSensor(
    "Total Reactive Power 2",
    0x1015,
    1,
    mqtt_topic_suffix="total/reactive_power2",
    unit="Var",
    groups=["igen_dtsd422"],
)
total_apparent_power_sensor = SignedMagnitudeDoubleRegisterSensor(
    "Total Apparent Power",
    0x1D,
    1,
    mqtt_topic_suffix="total/apparent_power",
    unit="VA",
    groups=["igen_dtsd422"],
)
total_apparent_power2_sensor = SignedMagnitudeDoubleRegisterSensor(
    "Total Apparent Power 2",
    0x101D,
    1,
    mqtt_topic_suffix="total/apparent_power2",
    unit="VA",
    groups=["igen_dtsd422"],
)
total_positive_energy_sensor = SingleRegisterSensor(
    "Total Positive Energy",
    0x2B,
    0.01,
    mqtt_topic_suffix="total/positive_energy",
    unit="kWh",
    groups=["igen_dtsd422"],
)
total_positive_energy2_sensor = SingleRegisterSensor(
    "Total Positive Energy 2",
    0x102B,
    0.01,
    mqtt_topic_suffix="total/positive_energy2",
    unit="kWh",
    groups=["igen_dtsd422"],
)
total_negative_energy_sensor = SingleRegisterSensor(
    "Total Negative Energy",
    0x35,
    0.01,
    mqtt_topic_suffix="total/negative_energy",
    unit="kWh",
    groups=["igen_dtsd422"],
    print_format="{:0.2f}",
)
total_negative_energy2_sensor = SingleRegisterSensor(
    "Total Negative Energy 2",
    0x1035,
    0.01,
    mqtt_topic_suffix="total/negative_energy2",
    unit="kWh",
    groups=["igen_dtsd422"],
    print_format="{:0.2f}",
)
total_power_factor_sensor = SignedMagnitudeSingleRegisterSensor(
    "Power Factor",
    0x25,
    0.001,
    mqtt_topic_suffix="total/power_factor",
    groups=["igen_dtsd422"],
)
total_power_factor2_sensor = SignedMagnitudeSingleRegisterSensor(
    "Power Factor 2",
    0x1025,
    0.001,
    mqtt_topic_suffix="total/power_factor2",
    groups=["igen_dtsd422"],
)
total_frequency_sensor = SingleRegisterSensor(
    "Frequency",
    0x29,
    0.01,
    mqtt_topic_suffix="total/frequency",
    unit="Hz",
    groups=["igen_dtsd422"],
    print_format="{:0.2f}",
)
total_frequency2_sensor = SingleRegisterSensor(
    "Frequency 2",
    0x1029,
    0.01,
    mqtt_topic_suffix="total/frequency2",
    unit="Hz",
    groups=["igen_dtsd422"],
    print_format="{:0.2f}",
)


igen_dtsd422_sensors = [
    ct1_voltage_sensor,
    ct1_current_sensor,
    ct1_active_power_sensor,
    ct1_reactive_power_sensor,
    ct1_apparent_power_sensor,
    ct1_power_factor_sensor,
    ct1_total_positive_energy,
    ct1_total_negative_energy,
    ct2_voltage_sensor,
    ct2_current_sensor,
    ct2_active_power_sensor,
    ct2_reactive_power_sensor,
    ct2_apparent_power_sensor,
    ct2_power_factor_sensor,
    ct2_total_positive_energy,
    ct2_total_negative_energy,
    ct3_voltage_sensor,
    ct3_current_sensor,
    ct3_active_power_sensor,
    ct3_reactive_power_sensor,
    ct3_apparent_power_sensor,
    ct3_power_factor_sensor,
    ct3_total_positive_energy,
    ct3_total_negative_energy,
    ct4_voltage_sensor,
    ct4_current_sensor,
    ct4_active_power_sensor,
    ct4_reactive_power_sensor,
    ct4_apparent_power_sensor,
    ct4_power_factor_sensor,
    ct4_total_positive_energy,
    ct4_total_negative_energy,
    ct5_voltage_sensor,
    ct5_current_sensor,
    ct5_active_power_sensor,
    ct5_reactive_power_sensor,
    ct5_apparent_power_sensor,
    ct5_power_factor_sensor,
    ct5_total_positive_energy,
    ct5_total_negative_energy,
    ct6_voltage_sensor,
    ct6_current_sensor,
    ct6_active_power_sensor,
    ct6_reactive_power_sensor,
    ct6_apparent_power_sensor,
    ct6_power_factor_sensor,
    ct6_total_positive_energy,
    ct6_total_negative_energy,
    total_active_power_sensor,
    total_active_power2_sensor,
    total_reactive_power_sensor,
    total_reactive_power2_sensor,
    total_apparent_power_sensor,
    total_apparent_power2_sensor,
    total_positive_energy_sensor,
    total_positive_energy2_sensor,
    total_negative_energy_sensor,
    total_negative_energy2_sensor,
    total_power_factor_sensor,
    total_power_factor2_sensor,
    total_frequency_sensor,
    total_frequency2_sensor,
]

igen_dtsd422_register_ranges = [
    SensorRegisterRange(group="igen_dtsd422", first_reg_address=0x01, last_reg_address=0x64),
    SensorRegisterRange(group="igen_dtsd422", first_reg_address=0x65, last_reg_address=0xA1),
    SensorRegisterRange(group="igen_dtsd422", first_reg_address=0x1001, last_reg_address=0x1064),
    SensorRegisterRange(group="igen_dtsd422", first_reg_address=0x1065, last_reg_address=0x10A1),
]
