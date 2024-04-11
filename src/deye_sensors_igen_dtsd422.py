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
    DoubleRegisterSensor,
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
ct1_total_positive_energy = DoubleRegisterSensor(
    "Total Positive Energy CT1",
    0x3E,
    0.01,
    mqtt_topic_suffix="ct1/total_positive_energy",
    unit="kWh",
    groups=["igen_dtsd422"],
    print_format="{:0.2f}",
    low_word_first=False,
)
ct1_total_negative_energy = DoubleRegisterSensor(
    "Total Negative Energy CT1",
    0x48,
    0.01,
    mqtt_topic_suffix="ct1/total_negative_energy",
    unit="kWh",
    groups=["igen_dtsd422"],
    print_format="{:0.2f}",
    low_word_first=False,
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
ct2_total_positive_energy = DoubleRegisterSensor(
    "Total Positive Energy CT2",
    0x52,
    0.01,
    mqtt_topic_suffix="ct2/total_positive_energy",
    unit="kWh",
    groups=["igen_dtsd422"],
    print_format="{:0.2f}",
    low_word_first=False,
)
ct2_total_negative_energy = DoubleRegisterSensor(
    "Total Negative Energy CT2",
    0x5C,
    0.01,
    mqtt_topic_suffix="ct2/total_negative_energy",
    unit="kWh",
    groups=["igen_dtsd422"],
    print_format="{:0.2f}",
    low_word_first=False,
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
ct3_total_positive_energy = DoubleRegisterSensor(
    "Total Positive Energy CT3",
    0x66,
    0.01,
    mqtt_topic_suffix="ct3/total_positive_energy",
    unit="kWh",
    groups=["igen_dtsd422"],
    print_format="{:0.2f}",
    low_word_first=False,
)
ct3_total_negative_energy = DoubleRegisterSensor(
    "Total Negative Energy CT3",
    0x70,
    0.01,
    mqtt_topic_suffix="ct3/total_negative_energy",
    unit="kWh",
    groups=["igen_dtsd422"],
    print_format="{:0.2f}",
    low_word_first=False,
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
ct4_total_positive_energy = DoubleRegisterSensor(
    "Total Positive Energy CT4",
    0x103E,
    0.01,
    mqtt_topic_suffix="ct4/total_positive_energy",
    unit="kWh",
    groups=["igen_dtsd422"],
    print_format="{:0.2f}",
    low_word_first=False,
)
ct4_total_negative_energy = DoubleRegisterSensor(
    "Total Negative Energy CT4",
    0x1048,
    0.01,
    mqtt_topic_suffix="ct4/total_negative_energy",
    unit="kWh",
    groups=["igen_dtsd422"],
    print_format="{:0.2f}",
    low_word_first=False,
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
ct5_total_positive_energy = DoubleRegisterSensor(
    "Total Positive Energy CT5",
    0x1052,
    0.01,
    mqtt_topic_suffix="ct5/total_positive_energy",
    unit="kWh",
    groups=["igen_dtsd422"],
    print_format="{:0.2f}",
    low_word_first=False,
)
ct5_total_negative_energy = DoubleRegisterSensor(
    "Total Negative Energy CT5",
    0x105C,
    0.01,
    mqtt_topic_suffix="ct5/total_negative_energy",
    unit="kWh",
    groups=["igen_dtsd422"],
    print_format="{:0.2f}",
    low_word_first=False,
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
ct6_total_positive_energy = DoubleRegisterSensor(
    "Total Positive Energy CT6",
    0x1066,
    0.01,
    mqtt_topic_suffix="ct6/total_positive_energy",
    unit="kWh",
    groups=["igen_dtsd422"],
    print_format="{:0.2f}",
    low_word_first=False,
)
ct6_total_negative_energy = DoubleRegisterSensor(
    "Total Negative Energy CT6",
    0x1070,
    0.01,
    mqtt_topic_suffix="ct6/total_negative_energy",
    unit="kWh",
    groups=["igen_dtsd422"],
    print_format="{:0.2f}",
    low_word_first=False,
)

# Total
ch1_total_active_power_sensor = SignedMagnitudeDoubleRegisterSensor(
    "Total Active Power (1st channel)",
    0x0D,
    1,
    mqtt_topic_suffix="total/1/active_power",
    unit="W",
    groups=["igen_dtsd422"],
)
ch2_total_active_power_sensor = SignedMagnitudeDoubleRegisterSensor(
    "Total Active Power (2nd channel)",
    0x100D,
    1,
    mqtt_topic_suffix="total/2/active_power",
    unit="W",
    groups=["igen_dtsd422"],
)
ch1_total_reactive_power_sensor = SignedMagnitudeDoubleRegisterSensor(
    "Total Reactive Power (1st channel)",
    0x15,
    1,
    mqtt_topic_suffix="total/1/reactive_power",
    unit="Var",
    groups=["igen_dtsd422"],
)
ch2_total_reactive_power_sensor = SignedMagnitudeDoubleRegisterSensor(
    "Total Reactive Power (2nd channel)",
    0x1015,
    1,
    mqtt_topic_suffix="total/2/reactive_power",
    unit="Var",
    groups=["igen_dtsd422"],
)
ch1_total_apparent_power_sensor = SignedMagnitudeDoubleRegisterSensor(
    "Total Apparent Power (1st channel)",
    0x1D,
    1,
    mqtt_topic_suffix="total/1/apparent_power",
    unit="VA",
    groups=["igen_dtsd422"],
)
ch2_total_apparent_power_sensor = SignedMagnitudeDoubleRegisterSensor(
    "Total Apparent Power (2nd channel)",
    0x101D,
    1,
    mqtt_topic_suffix="total/2/apparent_power",
    unit="VA",
    groups=["igen_dtsd422"],
)
ch1_total_positive_energy_sensor = DoubleRegisterSensor(
    "Total Positive Energy (1st channel)",
    0x2A,
    0.01,
    mqtt_topic_suffix="total/1/positive_energy",
    unit="kWh",
    groups=["igen_dtsd422"],
    low_word_first=False,
)
ch2_total_positive_energy_sensor = DoubleRegisterSensor(
    "Total Positive Energy (2nd channel)",
    0x102A,
    0.01,
    mqtt_topic_suffix="total/2/positive_energy",
    unit="kWh",
    groups=["igen_dtsd422"],
    low_word_first=False,
)
ch1_total_negative_energy_sensor = DoubleRegisterSensor(
    "Total Negative Energy (1st channel)",
    0x34,
    0.01,
    mqtt_topic_suffix="total/1/negative_energy",
    unit="kWh",
    groups=["igen_dtsd422"],
    print_format="{:0.2f}",
    low_word_first=False,
)
ch2_total_negative_energy_sensor = DoubleRegisterSensor(
    "Total Negative Energy (2nd channel)",
    0x1034,
    0.01,
    mqtt_topic_suffix="total/2/negative_energy",
    unit="kWh",
    groups=["igen_dtsd422"],
    print_format="{:0.2f}",
    low_word_first=False,
)
ch1_total_power_factor_sensor = SignedMagnitudeSingleRegisterSensor(
    "Power Factor (1st channel)",
    0x25,
    0.001,
    mqtt_topic_suffix="total/1/power_factor",
    groups=["igen_dtsd422"],
)
ch2_total_power_factor_sensor = SignedMagnitudeSingleRegisterSensor(
    "Power Factor (2nd channel)",
    0x1025,
    0.001,
    mqtt_topic_suffix="total/2/power_factor",
    groups=["igen_dtsd422"],
)
ch1_total_frequency_sensor = SingleRegisterSensor(
    "Frequency (1st channel)",
    0x29,
    0.01,
    mqtt_topic_suffix="total/1/frequency",
    unit="Hz",
    groups=["igen_dtsd422"],
    print_format="{:0.2f}",
)
ch2_total_frequency_sensor = SingleRegisterSensor(
    "Frequency (2nd channel)",
    0x1029,
    0.01,
    mqtt_topic_suffix="total/2/frequency",
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
    ch1_total_active_power_sensor,
    ch2_total_active_power_sensor,
    ch1_total_reactive_power_sensor,
    ch2_total_reactive_power_sensor,
    ch1_total_apparent_power_sensor,
    ch2_total_apparent_power_sensor,
    ch1_total_positive_energy_sensor,
    ch2_total_positive_energy_sensor,
    ch1_total_negative_energy_sensor,
    ch2_total_negative_energy_sensor,
    ch1_total_power_factor_sensor,
    ch2_total_power_factor_sensor,
    ch1_total_frequency_sensor,
    ch2_total_frequency_sensor,
]

igen_dtsd422_register_ranges = [
    SensorRegisterRange(group="igen_dtsd422", first_reg_address=0x01, last_reg_address=0x64),
    SensorRegisterRange(group="igen_dtsd422", first_reg_address=0x65, last_reg_address=0xA1),
    SensorRegisterRange(group="igen_dtsd422", first_reg_address=0x1001, last_reg_address=0x1064),
    SensorRegisterRange(group="igen_dtsd422", first_reg_address=0x1065, last_reg_address=0x10A1),
]
