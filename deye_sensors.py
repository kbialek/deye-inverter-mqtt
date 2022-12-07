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

from deye_sensor import SingleRegisterSensor, ComputedPowerSensor

# AC Phase 1
phase1_voltage_sensor = SingleRegisterSensor("Phase1 Voltage", 0x49, 0.1, mqtt_topic_suffix='ac/l1/voltage')
phase1_current_sensor = SingleRegisterSensor("Phase1 Current", 0x4c, 0.1, mqtt_topic_suffix='ac/l1/current')
phase1_power_sensor = ComputedPowerSensor("Phase1 Power", phase1_voltage_sensor,
                                          phase1_current_sensor, mqtt_topic_suffix='ac/l1/power')

# AC Phase 2
phase2_voltage_sensor = SingleRegisterSensor("Phase2 Voltage", 0x4a, 0.1, mqtt_topic_suffix='ac/l2/voltage')
phase2_current_sensor = SingleRegisterSensor("Phase2 Current", 0x4d, 0.1, mqtt_topic_suffix='ac/l2/current')
phase2_power_sensor = ComputedPowerSensor("Phase2 Power", phase2_voltage_sensor,
                                          phase2_current_sensor, mqtt_topic_suffix='ac/l2/power')

# AC Phase 3
phase3_voltage_sensor = SingleRegisterSensor("Phase3 Voltage", 0x4b, 0.1, mqtt_topic_suffix='ac/l3/voltage')
phase3_current_sensor = SingleRegisterSensor("Phase3 Current", 0x4e, 0.1, mqtt_topic_suffix='ac/l3/current')
phase3_power_sensor = ComputedPowerSensor("Phase3 Power", phase3_voltage_sensor,
                                          phase3_current_sensor, mqtt_topic_suffix='ac/l3/power')

# AC Freq
ac_freq_sensor = SingleRegisterSensor("AC Freq", 0x4f, 0.01, mqtt_topic_suffix='ac/freq')

# Production today
production_today_sensor = SingleRegisterSensor("Production today", 0x3c, 0.1, mqtt_topic_suffix='day_energy')
uptime_sensor = SingleRegisterSensor("Uptime", 0x3e, 1, mqtt_topic_suffix='uptime')

# DC PV1
pv1_voltage_sensor = SingleRegisterSensor("PV1 Voltage", 0x6d, 0.1, mqtt_topic_suffix='dc/pv1/voltage')
pv1_current_sensor = SingleRegisterSensor("PV1 Current", 0x6e, 0.1, mqtt_topic_suffix='dc/pv1/current')
pv1_power_sensor = ComputedPowerSensor("PV1 Power", pv1_voltage_sensor,
                                       pv1_current_sensor, mqtt_topic_suffix='dc/pv1/power')

# DC PV2
pv2_voltage_sensor = SingleRegisterSensor("PV2 Voltage", 0x6f, 0.1, mqtt_topic_suffix='dc/pv2/voltage')
pv2_current_sensor = SingleRegisterSensor("PV2 Current", 0x70, 0.1, mqtt_topic_suffix='dc/pv2/current')
pv2_power_sensor = ComputedPowerSensor("PV2 Power", pv2_voltage_sensor,
                                       pv2_current_sensor, mqtt_topic_suffix='dc/pv2/power')

# DC PV3
pv3_voltage_sensor = SingleRegisterSensor("PV3 Voltage", 0x71, 0.1, mqtt_topic_suffix='dc/pv3/voltage')
pv3_current_sensor = SingleRegisterSensor("PV3 Current", 0x72, 0.1, mqtt_topic_suffix='dc/pv3/current')
pv3_power_sensor = ComputedPowerSensor("PV3 Power", pv3_voltage_sensor,
                                       pv3_current_sensor, mqtt_topic_suffix='dc/pv3/power')

# DC PV4
pv4_voltage_sensor = SingleRegisterSensor("PV4 Voltage", 0x73, 0.1, mqtt_topic_suffix='dc/pv4/voltage')
pv4_current_sensor = SingleRegisterSensor("PV4 Current", 0x74, 0.1, mqtt_topic_suffix='dc/pv4/current')
pv4_power_sensor = ComputedPowerSensor("PV4 Power", pv4_voltage_sensor,
                                       pv4_current_sensor, mqtt_topic_suffix='dc/pv4/power')

# Power sensors
operating_power_sensor = SingleRegisterSensor("Operating Power", 0x50, 0.1, mqtt_topic_suffix='operating_power')
dc_power_sensor = SingleRegisterSensor("DC Total Power", 0x52, 0.1, mqtt_topic_suffix='dc/total_power')
ac_apparent_power_sensor = SingleRegisterSensor("AC Apparent Power", 0x54, 0.1, mqtt_topic_suffix='ac/apparent_power')
ac_active_power_sensor = SingleRegisterSensor("AC Active Power", 0x56, 0.1, mqtt_topic_suffix='ac/active_power')
ac_reactive_power_sensor = SingleRegisterSensor("AC Reactive Power", 0x58, 0.1, mqtt_topic_suffix='ac/reactive_power')

# Temperature sensors
radiator_temp_sensor = SingleRegisterSensor("Radiator temperature", 0x5a, 0.1,
                                            offset=-100, mqtt_topic_suffix='radiator_temp')
igbt_temp_sensor = SingleRegisterSensor("IGBT temperature", 0x5b, 0.1, offset=-100, mqtt_topic_suffix='igbt_temp')

sensor_list = [
    production_today_sensor,
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
    pv2_voltage_sensor,
    pv2_current_sensor,
    pv2_power_sensor,
    pv3_voltage_sensor,
    pv3_current_sensor,
    pv3_power_sensor,
    pv4_voltage_sensor,
    pv4_current_sensor,
    pv4_power_sensor,
    dc_power_sensor,
    operating_power_sensor,
    ac_apparent_power_sensor,
    ac_active_power_sensor,
    ac_reactive_power_sensor,
    radiator_temp_sensor,
    igbt_temp_sensor
]
