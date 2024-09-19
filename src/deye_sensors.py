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
    ComputedPowerSensor,
    DoubleRegisterSensor,
    ComputedSumSensor,
    SensorRegisterRange,
)

from deye_sensors_deye_sg04lp3 import deye_sg04lp3_sensors, deye_sg04lp3_register_ranges
from deye_sensors_deye_sg01hp3 import deye_sg01hp3_sensors, deye_sg01hp3_register_ranges
from deye_sensors_igen_dtsd422 import igen_dtsd422_sensors, igen_dtsd422_register_ranges
from deye_sensors_deye_hybrid import deye_hybrid_sensors, deye_hybrid_register_ranges
from deye_sensors_settings import deye_settings_sensors, deye_settings_register_ranges
from deye_sensors_aggregated import aggregated_sensor_list

# AC Phase 1
phase1_voltage_sensor = SingleRegisterSensor(
    "Phase1 Voltage", 0x49, 0.1, mqtt_topic_suffix="ac/l1/voltage", unit="V", groups=["string", "micro"]
)
phase1_current_sensor = SingleRegisterSensor(
    "Phase1 Current", 0x4C, 0.1, mqtt_topic_suffix="ac/l1/current", unit="A", groups=["string", "micro"]
)
phase1_power_sensor = ComputedPowerSensor(
    "Phase1 Power",
    phase1_voltage_sensor,
    phase1_current_sensor,
    mqtt_topic_suffix="ac/l1/power",
    unit="W",
    groups=["string", "micro"],
)

# AC Phase 2
phase2_voltage_sensor = SingleRegisterSensor(
    "Phase2 Voltage", 0x4A, 0.1, mqtt_topic_suffix="ac/l2/voltage", unit="V", groups=["string"]
)
phase2_current_sensor = SingleRegisterSensor(
    "Phase2 Current", 0x4D, 0.1, mqtt_topic_suffix="ac/l2/current", unit="A", groups=["string"]
)
phase2_power_sensor = ComputedPowerSensor(
    "Phase2 Power",
    phase2_voltage_sensor,
    phase2_current_sensor,
    mqtt_topic_suffix="ac/l2/power",
    unit="W",
    groups=["string"],
)

# AC Phase 3
phase3_voltage_sensor = SingleRegisterSensor(
    "Phase3 Voltage", 0x4B, 0.1, mqtt_topic_suffix="ac/l3/voltage", unit="V", groups=["string"]
)
phase3_current_sensor = SingleRegisterSensor(
    "Phase3 Current", 0x4E, 0.1, mqtt_topic_suffix="ac/l3/current", unit="A", groups=["string"]
)
phase3_power_sensor = ComputedPowerSensor(
    "Phase3 Power",
    phase3_voltage_sensor,
    phase3_current_sensor,
    mqtt_topic_suffix="ac/l3/power",
    unit="W",
    groups=["string"],
)

# AC Freq
ac_freq_sensor = SingleRegisterSensor(
    "AC Freq", 0x4F, 0.01, mqtt_topic_suffix="ac/freq", unit="Hz", groups=["string", "micro"]
)

# Production today
production_today_sensor = SingleRegisterSensor(
    "Production today", 0x3C, 0.1, mqtt_topic_suffix="day_energy", unit="kWh", groups=["string", "micro"]
).reset_daily()
uptime_sensor = SingleRegisterSensor(
    "Uptime", 0x3E, 1, mqtt_topic_suffix="uptime", unit="minutes", groups=["string", "micro"]
)

# DC PV1
pv1_voltage_sensor = SingleRegisterSensor(
    "PV1 Voltage", 0x6D, 0.1, mqtt_topic_suffix="dc/pv1/voltage", unit="V", groups=["string", "micro"]
)
pv1_current_sensor = SingleRegisterSensor(
    "PV1 Current", 0x6E, 0.1, mqtt_topic_suffix="dc/pv1/current", unit="A", groups=["string", "micro"]
)
pv1_power_sensor = ComputedPowerSensor(
    "PV1 Power",
    pv1_voltage_sensor,
    pv1_current_sensor,
    mqtt_topic_suffix="dc/pv1/power",
    unit="W",
    groups=["string", "micro"],
)
pv1_daily_sensor = SingleRegisterSensor(
    "PV1 Production today", 0x41, 0.1, mqtt_topic_suffix="dc/pv1/day_energy", unit="kWh", groups=["micro"]
).reset_daily()
pv1_total_sensor = DoubleRegisterSensor(
    "PV1 Total", 0x45, 0.1, mqtt_topic_suffix="dc/pv1/total_energy", unit="kWh", groups=["micro"]
)

# DC PV2
pv2_voltage_sensor = SingleRegisterSensor(
    "PV2 Voltage", 0x6F, 0.1, mqtt_topic_suffix="dc/pv2/voltage", unit="V", groups=["string", "micro"]
)
pv2_current_sensor = SingleRegisterSensor(
    "PV2 Current", 0x70, 0.1, mqtt_topic_suffix="dc/pv2/current", unit="A", groups=["string", "micro"]
)
pv2_power_sensor = ComputedPowerSensor(
    "PV2 Power",
    pv2_voltage_sensor,
    pv2_current_sensor,
    mqtt_topic_suffix="dc/pv2/power",
    unit="W",
    groups=["string", "micro"],
)
pv2_daily_sensor = SingleRegisterSensor(
    "PV2 Production today", 0x42, 0.1, mqtt_topic_suffix="dc/pv2/day_energy", unit="kWh", groups=["micro"]
).reset_daily()
pv2_total_sensor = DoubleRegisterSensor(
    "PV2 Total", 0x47, 0.1, mqtt_topic_suffix="dc/pv2/total_energy", unit="kWh", groups=["micro"]
)

# DC PV3
pv3_voltage_sensor = SingleRegisterSensor(
    "PV3 Voltage", 0x71, 0.1, mqtt_topic_suffix="dc/pv3/voltage", unit="V", groups=["string", "micro"]
)
pv3_current_sensor = SingleRegisterSensor(
    "PV3 Current", 0x72, 0.1, mqtt_topic_suffix="dc/pv3/current", unit="A", groups=["string", "micro"]
)
pv3_power_sensor = ComputedPowerSensor(
    "PV3 Power",
    pv3_voltage_sensor,
    pv3_current_sensor,
    mqtt_topic_suffix="dc/pv3/power",
    unit="W",
    groups=["string", "micro"],
)
pv3_daily_sensor = SingleRegisterSensor(
    "PV3 Production today", 0x43, 0.1, mqtt_topic_suffix="dc/pv3/day_energy", unit="kWh", groups=["micro"]
).reset_daily()
pv3_total_sensor = DoubleRegisterSensor(
    "PV3 Total", 0x4A, 0.1, mqtt_topic_suffix="dc/pv3/total_energy", unit="kWh", groups=["micro"]
)

# DC PV4
pv4_voltage_sensor = SingleRegisterSensor(
    "PV4 Voltage", 0x73, 0.1, mqtt_topic_suffix="dc/pv4/voltage", unit="V", groups=["string", "micro"]
)
pv4_current_sensor = SingleRegisterSensor(
    "PV4 Current", 0x74, 0.1, mqtt_topic_suffix="dc/pv4/current", unit="A", groups=["string", "micro"]
)
pv4_power_sensor = ComputedPowerSensor(
    "PV4 Power",
    pv4_voltage_sensor,
    pv4_current_sensor,
    mqtt_topic_suffix="dc/pv4/power",
    unit="W",
    groups=["string", "micro"],
)
pv4_daily_sensor = SingleRegisterSensor(
    "PV4 Production today", 0x44, 0.1, mqtt_topic_suffix="dc/pv4/day_energy", unit="kWh", groups=["micro"]
).reset_daily()
pv4_total_sensor = DoubleRegisterSensor(
    "PV4 Total", 0x4D, 0.1, mqtt_topic_suffix="dc/pv4/total_energy", unit="kWh", groups=["micro"]
)

# Power sensors
operating_power_sensor = SingleRegisterSensor(
    "Operating Power", 0x50, 0.1, mqtt_topic_suffix="operating_power", unit="W", groups=["string", "micro"]
)
string_dc_power_sensor = SingleRegisterSensor(
    "DC Total Power", 0x52, 0.1, mqtt_topic_suffix="dc/total_power", unit="W", groups=["string"]
)
micro_dc_power_sensor = ComputedSumSensor(
    "DC Total Power",
    [pv1_power_sensor, pv2_power_sensor, pv3_power_sensor, pv4_power_sensor],
    mqtt_topic_suffix="dc/total_power",
    unit="W",
    groups=["micro"],
)
ac_apparent_power_sensor = SingleRegisterSensor(
    "AC Apparent Power", 0x54, 0.1, mqtt_topic_suffix="ac/apparent_power", unit="W", groups=["string"]
)
ac_active_power_sensor = DoubleRegisterSensor(
    "AC Active Power", 0x56, 0.1, mqtt_topic_suffix="ac/active_power", unit="W", groups=["string", "micro"]
)
ac_reactive_power_sensor = SingleRegisterSensor(
    "AC Reactive Power", 0x58, 0.1, mqtt_topic_suffix="ac/reactive_power", unit="W", groups=["string"]
)
production_total_sensor = DoubleRegisterSensor(
    "Production Total", 0x3F, 0.1, mqtt_topic_suffix="total_energy", unit="kWh", groups=["string", "micro"]
).use_as_readiness_check()

# Temperature sensors
string_radiator_temp_sensor = SingleRegisterSensor(
    "Radiator temperature", 0x5A, 0.1, offset=-100, mqtt_topic_suffix="radiator_temp", unit="°C", groups=["string"]
)
micro_radiator_temp_sensor = SingleRegisterSensor(
    "Radiator temperature", 0x5A, 0.01, offset=-10, mqtt_topic_suffix="radiator_temp", unit="°C", groups=["micro"]
)
igbt_temp_sensor = SingleRegisterSensor(
    "IGBT temperature", 0x5B, 0.1, offset=-100, mqtt_topic_suffix="igbt_temp", unit="°C", groups=["string"]
)

sensor_list = (
    [
        production_today_sensor,
        production_total_sensor,
        phase1_voltage_sensor,
        phase1_current_sensor,
        phase1_power_sensor,
        phase2_voltage_sensor,
        phase2_current_sensor,
        phase2_power_sensor,
        phase3_voltage_sensor,
        phase3_current_sensor,
        phase3_power_sensor,
        ac_freq_sensor,
        uptime_sensor,
        pv1_voltage_sensor,
        pv1_current_sensor,
        pv1_power_sensor,
        pv1_daily_sensor,
        pv1_total_sensor,
        pv2_voltage_sensor,
        pv2_current_sensor,
        pv2_power_sensor,
        pv2_daily_sensor,
        pv2_total_sensor,
        pv3_voltage_sensor,
        pv3_current_sensor,
        pv3_power_sensor,
        pv3_daily_sensor,
        pv3_total_sensor,
        pv4_voltage_sensor,
        pv4_current_sensor,
        pv4_power_sensor,
        pv4_daily_sensor,
        pv4_total_sensor,
        string_dc_power_sensor,
        micro_dc_power_sensor,
        operating_power_sensor,
        ac_apparent_power_sensor,
        ac_active_power_sensor,
        ac_reactive_power_sensor,
        string_radiator_temp_sensor,
        micro_radiator_temp_sensor,
        igbt_temp_sensor,
    ]
    + deye_sg04lp3_sensors
    + igen_dtsd422_sensors
    + deye_hybrid_sensors
    + deye_settings_sensors
    + deye_sg01hp3_sensors
    + aggregated_sensor_list
)

sensor_register_ranges = (
    [
        SensorRegisterRange(group="string", first_reg_address=0x3C, last_reg_address=0x74),
        SensorRegisterRange(group="micro", first_reg_address=0x3C, last_reg_address=0x74),
    ]
    + deye_sg04lp3_register_ranges
    + igen_dtsd422_register_ranges
    + deye_hybrid_register_ranges
    + deye_settings_register_ranges
    + deye_sg01hp3_register_ranges
)
