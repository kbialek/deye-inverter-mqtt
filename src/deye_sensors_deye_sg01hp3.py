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
    ComputedSumSensor,
    SensorRegisterRange,
    EnumValueSensor,
    ComputedBooleanSensor,
)

deye_sg01hp3_inverter_500 = EnumValueSensor(
    "Running status",
    500,
    mqtt_topic_suffix="inverter/status",
    groups=["deye_sg01hp3"],
    enum_values={0: "standby", 1: "selfcheck", 2: "normal", 3: "alarm", 4: "fault"},
)

deye_sg01hp3_inverter_552 = SingleRegisterSensor(
    "AC relays status",
    552,
    1,
    mqtt_topic_suffix="ac/relay_status",
    unit="",
    print_format="{:0>2X}",
    signed=False,
    groups=["deye_sg01hp3"],
)

ongrid_status_sensor = ComputedBooleanSensor(
    "On-grid",
    bitarray_sensor=deye_sg01hp3_inverter_552,
    mask=0x4,
    mqtt_topic_suffix="ac/ongrid",
    groups=["deye_sg01hp3"],
)

deye_sg01hp3_solar_672 = SingleRegisterSensor(
    "PV1 Power", 672, 10, mqtt_topic_suffix="dc/pv1/power", unit="W", signed=False, groups=["deye_sg01hp3"]
)

deye_sg01hp3_solar_673 = SingleRegisterSensor(
    "PV2 Power", 673, 10, mqtt_topic_suffix="dc/pv2/power", unit="W", signed=False, groups=["deye_sg01hp3"]
)

deye_sg01hp3_solar_674 = SingleRegisterSensor(
    "PV3 Power", 674, 10, mqtt_topic_suffix="dc/pv3/power", unit="W", signed=False, groups=["deye_sg01hp3"]
)

deye_sg01hp3_solar_675 = SingleRegisterSensor(
    "PV4 Power", 675, 10, mqtt_topic_suffix="dc/pv4/power", unit="W", signed=False, groups=["deye_sg01hp3"]
)

deye_sg01hp3_solar_676 = SingleRegisterSensor(
    "PV1 Voltage", 676, 0.1, mqtt_topic_suffix="dc/pv1/voltage", unit="V", signed=False, groups=["deye_sg01hp3"]
)

deye_sg01hp3_solar_678 = SingleRegisterSensor(
    "PV2 Voltage", 678, 0.1, mqtt_topic_suffix="dc/pv2/voltage", unit="V", signed=False, groups=["deye_sg01hp3"]
)

deye_sg01hp3_solar_680 = SingleRegisterSensor(
    "PV3 Voltage", 680, 0.1, mqtt_topic_suffix="dc/pv3/voltage", unit="V", signed=False, groups=["deye_sg01hp3"]
)

deye_sg01hp3_solar_682 = SingleRegisterSensor(
    "PV4 Voltage", 682, 0.1, mqtt_topic_suffix="dc/pv4/voltage", unit="V", signed=False, groups=["deye_sg01hp3"]
)

deye_sg01hp3_solar_677 = SingleRegisterSensor(
    "PV1 Current", 677, 0.1, mqtt_topic_suffix="dc/pv1/current", unit="A", signed=False, groups=["deye_sg01hp3"]
)

deye_sg01hp3_solar_679 = SingleRegisterSensor(
    "PV2 Current", 679, 0.1, mqtt_topic_suffix="dc/pv2/current", unit="A", signed=False, groups=["deye_sg01hp3"]
)

deye_sg01hp3_solar_681 = SingleRegisterSensor(
    "PV3 Current", 681, 0.1, mqtt_topic_suffix="dc/pv3/current", unit="A", signed=False, groups=["deye_sg01hp3"]
)

deye_sg01hp3_solar_683 = SingleRegisterSensor(
    "PV4 Current", 683, 0.1, mqtt_topic_suffix="dc/pv4/current", unit="A", signed=False, groups=["deye_sg01hp3"]
)

deye_sg01hp3_solar_529 = SingleRegisterSensor(
    "Daily Production", 529, 0.1, mqtt_topic_suffix="day_energy", unit="kWh", signed=False, groups=["deye_sg01hp3"]
)

deye_sg01hp3_solar_534 = DoubleRegisterSensor(
    "Total Production", 534, 0.1, mqtt_topic_suffix="total_energy", unit="kWh", signed=False, groups=["deye_sg01hp3"]
)

deye_sg01hp3_battery_514 = SingleRegisterSensor(
    "Daily Battery Charge",
    514,
    0.1,
    mqtt_topic_suffix="battery/daily_charge",
    unit="kWh",
    signed=False,
    groups=["deye_sg01hp3_battery"],
)

deye_sg01hp3_battery_515 = SingleRegisterSensor(
    "Daily Battery Discharge",
    515,
    0.1,
    mqtt_topic_suffix="battery/daily_discharge",
    unit="kWh",
    signed=False,
    groups=["deye_sg01hp3_battery"],
)

deye_sg01hp3_battery_516 = DoubleRegisterSensor(
    "Total Battery Charge",
    516,
    0.1,
    mqtt_topic_suffix="battery/total_charge",
    unit="kWh",
    signed=False,
    groups=["deye_sg01hp3_battery"],
)

deye_sg01hp3_battery_518 = DoubleRegisterSensor(
    "Total Battery Discharge",
    518,
    0.1,
    mqtt_topic_suffix="battery/total_discharge",
    unit="kWh",
    signed=False,
    groups=["deye_sg01hp3_battery"],
)

deye_sg01hp3_battery1_590 = SingleRegisterSensor(
    "Battery1 Power",
    590,
    10,
    mqtt_topic_suffix="battery/1/power",
    unit="W",
    signed=True,
    groups=["deye_sg01hp3_battery"],
)

deye_sg01hp3_battery1_587 = SingleRegisterSensor(
    "Battery1 Voltage",
    587,
    0.1,
    mqtt_topic_suffix="battery/1/voltage",
    unit="V",
    signed=False,
    groups=["deye_sg01hp3_battery"],
)

deye_sg01hp3_battery1_588 = SingleRegisterSensor(
    "Battery1 SOC", 588, 1, mqtt_topic_suffix="battery/1/soc", unit="%", signed=False, groups=["deye_sg01hp3_battery"]
)

deye_sg01hp3_battery1_591 = SingleRegisterSensor(
    "Battery1 Current",
    591,
    0.01,
    mqtt_topic_suffix="battery/1/current",
    unit="A",
    signed=True,
    groups=["deye_sg01hp3_battery"],
)

deye_sg01hp3_battery1_586 = SingleRegisterSensor(
    "Battery1 Temperature",
    586,
    0.1,
    offset=-100.0,
    mqtt_topic_suffix="battery/1/temperature",
    unit="°C",
    signed=False,
    groups=["deye_sg01hp3_battery"],
)

deye_sg01hp3_battery2_589 = SingleRegisterSensor(
    "Battery2 SOC", 589, 1, mqtt_topic_suffix="battery/2/soc", unit="%", signed=False, groups=["deye_sg01hp3_battery"]
)

deye_sg01hp3_battery2_593 = SingleRegisterSensor(
    "Battery2 Voltage",
    593,
    0.1,
    mqtt_topic_suffix="battery/2/voltage",
    unit="V",
    signed=False,
    groups=["deye_sg01hp3_battery"],
)

deye_sg01hp3_battery2_594 = SingleRegisterSensor(
    "Battery2 Current",
    594,
    0.01,
    mqtt_topic_suffix="battery/2/current",
    unit="A",
    signed=True,
    groups=["deye_sg01hp3_battery"],
)

deye_sg01hp3_battery2_595 = SingleRegisterSensor(
    "Battery2 Power",
    595,
    10,
    mqtt_topic_suffix="battery/2/power",
    unit="W",
    signed=True,
    groups=["deye_sg01hp3_battery"],
)

deye_sg01hp3_battery2_596 = SingleRegisterSensor(
    "Battery2 Temperature",
    596,
    0.1,
    mqtt_topic_suffix="battery/2/temperature",
    unit="°C",
    signed=True,
    groups=["deye_sg01hp3_battery"],
)

deye_sg01hp3_grid_625 = SingleRegisterSensor(
    "Total Grid Power", 625, 1, mqtt_topic_suffix="ac/total_power", unit="W", signed=True, groups=["deye_sg01hp3"]
)

deye_sg01hp3_grid_598 = SingleRegisterSensor(
    "Grid Voltage L1", 598, 0.1, mqtt_topic_suffix="ac/l1/voltage", unit="V", signed=False, groups=["deye_sg01hp3"]
)

deye_sg01hp3_grid_599 = SingleRegisterSensor(
    "Grid Voltage L2", 599, 0.1, mqtt_topic_suffix="ac/l2/voltage", unit="V", signed=False, groups=["deye_sg01hp3"]
)

deye_sg01hp3_grid_600 = SingleRegisterSensor(
    "Grid Voltage L3", 600, 0.1, mqtt_topic_suffix="ac/l3/voltage", unit="V", signed=False, groups=["deye_sg01hp3"]
)

deye_sg01hp3_grid_604 = SingleRegisterSensor(
    "Internal CT L1 Power",
    604,
    1,
    mqtt_topic_suffix="ac/l1/ct/internal",
    unit="W",
    signed=True,
    groups=["deye_sg01hp3"],
)

deye_sg01hp3_grid_605 = SingleRegisterSensor(
    "Internal CT L2 Power",
    605,
    1,
    mqtt_topic_suffix="ac/l2/ct/internal",
    unit="W",
    signed=True,
    groups=["deye_sg01hp3"],
)

deye_sg01hp3_grid_606 = SingleRegisterSensor(
    "Internal CT L3 Power",
    606,
    1,
    mqtt_topic_suffix="ac/l3/ct/internal",
    unit="W",
    signed=True,
    groups=["deye_sg01hp3"],
)

deye_sg01hp3_grid_616 = SingleRegisterSensor(
    "External CT L1 Power",
    616,
    1,
    mqtt_topic_suffix="ac/l1/ct/external",
    unit="W",
    signed=True,
    groups=["deye_sg01hp3"],
)

deye_sg01hp3_grid_617 = SingleRegisterSensor(
    "External CT L2 Power",
    617,
    1,
    mqtt_topic_suffix="ac/l2/ct/external",
    unit="W",
    signed=True,
    groups=["deye_sg01hp3"],
)

deye_sg01hp3_grid_618 = SingleRegisterSensor(
    "External CT L3 Power",
    618,
    1,
    mqtt_topic_suffix="ac/l3/ct/external",
    unit="W",
    signed=True,
    groups=["deye_sg01hp3"],
)

deye_sg01hp3_grid_520 = SingleRegisterSensor(
    "Daily Energy Bought",
    520,
    0.1,
    mqtt_topic_suffix="ac/daily_energy_bought",
    unit="kWh",
    signed=False,
    groups=["deye_sg01hp3"],
)

deye_sg01hp3_grid_522 = DoubleRegisterSensor(
    "Total Energy Bought",
    522,
    0.1,
    mqtt_topic_suffix="ac/total_energy_bought",
    unit="kWh",
    signed=False,
    groups=["deye_sg01hp3"],
)

deye_sg01hp3_grid_521 = SingleRegisterSensor(
    "Daily Energy Sold",
    521,
    0.1,
    mqtt_topic_suffix="ac/daily_energy_sold",
    unit="kWh",
    signed=False,
    groups=["deye_sg01hp3"],
)

deye_sg01hp3_grid_524 = DoubleRegisterSensor(
    "Total Energy Sold",
    524,
    0.1,
    mqtt_topic_suffix="ac/total_energy_sold",
    unit="kWh",
    signed=False,
    groups=["deye_sg01hp3"],
)

deye_sg01hp3_upload_653 = SingleRegisterSensor(
    "Total Load Power",
    653,
    1,
    mqtt_topic_suffix="ac/ups/total_power",
    unit="W",
    signed=False,
    groups=["deye_sg01hp3_ups"],
)

deye_sg01hp3_upload_650 = SingleRegisterSensor(
    "Load L1 Power", 650, 1, mqtt_topic_suffix="ac/ups/l1/power", unit="W", signed=True, groups=["deye_sg01hp3_ups"]
)

deye_sg01hp3_upload_651 = SingleRegisterSensor(
    "Load L2 Power", 651, 1, mqtt_topic_suffix="ac/ups/l2/power", unit="W", signed=True, groups=["deye_sg01hp3_ups"]
)

deye_sg01hp3_upload_652 = SingleRegisterSensor(
    "Load L3 Power", 652, 1, mqtt_topic_suffix="ac/ups/l3/power", unit="W", signed=True, groups=["deye_sg01hp3_ups"]
)

deye_sg01hp3_upload_644 = SingleRegisterSensor(
    "Load Voltage L1",
    644,
    0.1,
    mqtt_topic_suffix="ac/ups/l1/voltage",
    unit="V",
    signed=False,
    groups=["deye_sg01hp3_ups"],
)

deye_sg01hp3_upload_645 = SingleRegisterSensor(
    "Load Voltage L2",
    645,
    0.1,
    mqtt_topic_suffix="ac/ups/l2/voltage",
    unit="V",
    signed=False,
    groups=["deye_sg01hp3_ups"],
)

deye_sg01hp3_upload_646 = SingleRegisterSensor(
    "Load Voltage L3",
    646,
    0.1,
    mqtt_topic_suffix="ac/ups/l3/voltage",
    unit="V",
    signed=False,
    groups=["deye_sg01hp3_ups"],
)

deye_sg01hp3_upload_526 = SingleRegisterSensor(
    "Daily Load Consumption",
    526,
    0.1,
    mqtt_topic_suffix="ac/ups/daily_energy",
    unit="kWh",
    signed=False,
    groups=["deye_sg01hp3_ups"],
)

deye_sg01hp3_upload_527 = DoubleRegisterSensor(
    "Total Load Consumption",
    527,
    0.1,
    mqtt_topic_suffix="ac/ups/total_energy",
    unit="kWh",
    signed=False,
    groups=["deye_sg01hp3_ups"],
)

deye_sg01hp3_inverter_630 = SingleRegisterSensor(
    "Current L1", 630, 0.01, mqtt_topic_suffix="ac/l1/current", unit="A", signed=True, groups=["deye_sg01hp3"]
)

deye_sg01hp3_inverter_631 = SingleRegisterSensor(
    "Current L2", 631, 0.01, mqtt_topic_suffix="ac/l2/current", unit="A", signed=True, groups=["deye_sg01hp3"]
)

deye_sg01hp3_inverter_632 = SingleRegisterSensor(
    "Current L3", 632, 0.01, mqtt_topic_suffix="ac/l3/current", unit="A", signed=True, groups=["deye_sg01hp3"]
)

deye_sg01hp3_inverter_633 = SingleRegisterSensor(
    "Inverter L1 Power", 633, 1, mqtt_topic_suffix="ac/l1/power", unit="W", signed=True, groups=["deye_sg01hp3"]
)

deye_sg01hp3_inverter_634 = SingleRegisterSensor(
    "Inverter L2 Power", 634, 1, mqtt_topic_suffix="ac/l2/power", unit="W", signed=True, groups=["deye_sg01hp3"]
)

deye_sg01hp3_inverter_635 = SingleRegisterSensor(
    "Inverter L3 Power", 635, 1, mqtt_topic_suffix="ac/l3/power", unit="W", signed=True, groups=["deye_sg01hp3"]
)

deye_sg01hp3_inverter_540 = SingleRegisterSensor(
    "DC Temperature",
    540,
    0.1,
    offset=-100.0,
    mqtt_topic_suffix="radiator_temp",
    unit="°C",
    signed=True,
    groups=["deye_sg01hp3"],
)

deye_sg01hp3_inverter_541 = SingleRegisterSensor(
    "AC Temperature",
    541,
    0.1,
    offset=-100.0,
    mqtt_topic_suffix="ac/temperature",
    unit="°C",
    signed=True,
    groups=["deye_sg01hp3"],
)

deye_sg01hp3_bms1_210 = SingleRegisterSensor(
    "BMS1 Charging Voltage",
    210,
    0.1,
    mqtt_topic_suffix="bms/1/charging_voltage",
    unit="V",
    signed=False,
    groups=["deye_sg01hp3_bms"],
)

deye_sg01hp3_bms1_211 = SingleRegisterSensor(
    "BMS1 Discharge Voltage",
    211,
    0.1,
    mqtt_topic_suffix="bms/1/discharge_voltage",
    unit="V",
    signed=False,
    groups=["deye_sg01hp3_bms"],
)

deye_sg01hp3_bms1_212 = SingleRegisterSensor(
    "BMS1 Charge Current Limit",
    212,
    1,
    mqtt_topic_suffix="bms/1/charge_current_limit",
    unit="A",
    signed=False,
    groups=["deye_sg01hp3_bms"],
)

deye_sg01hp3_bms1_213 = SingleRegisterSensor(
    "BMS1 Discharge Current Limit",
    213,
    1,
    mqtt_topic_suffix="bms/1/discharge_current_limit",
    unit="A",
    signed=False,
    groups=["deye_sg01hp3_bms"],
)

deye_sg01hp3_bms1_214 = SingleRegisterSensor(
    "BMS1 SOC",
    214,
    1,
    mqtt_topic_suffix="bms/1/soc",
    unit="%",
    signed=False,
    groups=["deye_sg01hp3_bms"],
)

deye_sg01hp3_bms1_215 = SingleRegisterSensor(
    "BMS1 Voltage",
    215,
    0.1,
    mqtt_topic_suffix="bms/1/voltage",
    unit="V",
    signed=False,
    groups=["deye_sg01hp3_bms"],
)

deye_sg01hp3_bms1_216 = SingleRegisterSensor(
    "BMS1 Current",
    216,
    0.1,
    mqtt_topic_suffix="bms/1/current",
    unit="A",
    signed=True,
    groups=["deye_sg01hp3_bms"],
)

deye_sg01hp3_bms1_217 = SingleRegisterSensor(
    "BMS1 Temp",
    217,
    0.1,
    offset=-100.0,
    mqtt_topic_suffix="bms/1/temp",
    unit="°C",
    signed=True,
    groups=["deye_sg01hp3_bms"],
)

deye_sg01hp3_bms1_218 = SingleRegisterSensor(
    "BMS1 Charging Max Current",
    218,
    1,
    mqtt_topic_suffix="bms/1/charging_max_current",
    unit="A",
    signed=True,
    groups=["deye_sg01hp3_bms"],
)

deye_sg01hp3_bms1_219 = SingleRegisterSensor(
    "BMS1 Discharge Max Current",
    219,
    1,
    mqtt_topic_suffix="bms/1/discharge_max_current",
    unit="A",
    signed=True,
    groups=["deye_sg01hp3_bms"],
)

deye_sg01hp3_bms2_241 = SingleRegisterSensor(
    "BMS2 Charging Voltage",
    241,
    0.1,
    mqtt_topic_suffix="bms/2/charging_voltage",
    unit="V",
    signed=False,
    groups=["deye_sg01hp3_bms"],
)

deye_sg01hp3_bms2_242 = SingleRegisterSensor(
    "BMS2 Discharge Voltage",
    242,
    0.1,
    mqtt_topic_suffix="bms/2/discharge_voltage",
    unit="V",
    signed=False,
    groups=["deye_sg01hp3_bms"],
)

deye_sg01hp3_bms2_243 = SingleRegisterSensor(
    "BMS2 Charge Current Limit",
    243,
    1,
    mqtt_topic_suffix="bms/2/charge_current_limit",
    unit="A",
    signed=False,
    groups=["deye_sg01hp3_bms"],
)

deye_sg01hp3_bms2_244 = SingleRegisterSensor(
    "BMS2 Discharge Current Limit",
    244,
    1,
    mqtt_topic_suffix="bms/2/discharge_current_limit",
    unit="A",
    signed=False,
    groups=["deye_sg01hp3_bms"],
)

deye_sg01hp3_bms2_245 = SingleRegisterSensor(
    "BMS2 SOC",
    245,
    1,
    mqtt_topic_suffix="bms/2/soc",
    unit="%",
    signed=False,
    groups=["deye_sg01hp3_bms"],
)

deye_sg01hp3_bms2_246 = SingleRegisterSensor(
    "BMS2 Voltage",
    246,
    0.1,
    mqtt_topic_suffix="bms/2/voltage",
    unit="V",
    signed=False,
    groups=["deye_sg01hp3_bms"],
)

deye_sg01hp3_bms2_247 = SingleRegisterSensor(
    "BMS2 Current",
    247,
    0.1,
    mqtt_topic_suffix="bms/2/current",
    unit="A",
    signed=True,
    groups=["deye_sg01hp3_bms"],
)

deye_sg01hp3_bms2_248 = SingleRegisterSensor(
    "BMS2 Temp",
    248,
    0.1,
    offset=-100.0,
    mqtt_topic_suffix="bms/2/temp",
    unit="°C",
    signed=True,
    groups=["deye_sg01hp3_bms"],
)

deye_sg01hp3_bms2_249 = SingleRegisterSensor(
    "BMS2 Charging Max Current",
    249,
    1,
    mqtt_topic_suffix="bms/2/charging_max_current",
    unit="A",
    signed=True,
    groups=["deye_sg01hp3_bms"],
)

deye_sg01hp3_bms2_250 = SingleRegisterSensor(
    "BMS2 Discharge Max Current",
    250,
    1,
    mqtt_topic_suffix="bms/2/discharge_max_current",
    unit="A",
    signed=True,
    groups=["deye_sg01hp3_bms"],
)

total_pv_power_sensor = ComputedSumSensor(
    "DC Total Power",
    [deye_sg01hp3_solar_672, deye_sg01hp3_solar_673, deye_sg01hp3_solar_674, deye_sg01hp3_solar_675],
    mqtt_topic_suffix="dc/total_power",
    unit="W",
    groups=["deye_sg01hp3"],
)


deye_sg01hp3_time_of_use_146 = SingleRegisterSensor(
    "Time of Use Weekly Selling Schedule",
    146,
    1,
    mqtt_topic_suffix="timeofuse/selling",
    unit="",
    signed=False,
    groups=["deye_sg01hp3_timeofuse"],
)

deye_sg01hp3_time_of_use_148 = SingleRegisterSensor(
    "Time of Use Time 1",
    148,
    1,
    mqtt_topic_suffix="timeofuse/time/1",
    unit="",
    signed=False,
    groups=["deye_sg01hp3_timeofuse"],
)

deye_sg01hp3_time_of_use_149 = SingleRegisterSensor(
    "Time of Use Time 2",
    149,
    1,
    mqtt_topic_suffix="timeofuse/time/2",
    unit="",
    signed=False,
    groups=["deye_sg01hp3_timeofuse"],
)

deye_sg01hp3_time_of_use_150 = SingleRegisterSensor(
    "Time of Use Time 3",
    150,
    1,
    mqtt_topic_suffix="timeofuse/time/3",
    unit="",
    signed=False,
    groups=["deye_sg01hp3_timeofuse"],
)

deye_sg01hp3_time_of_use_151 = SingleRegisterSensor(
    "Time of Use Time 4",
    151,
    1,
    mqtt_topic_suffix="timeofuse/time/4",
    unit="",
    signed=False,
    groups=["deye_sg01hp3_timeofuse"],
)

deye_sg01hp3_time_of_use_152 = SingleRegisterSensor(
    "Time of Use Time 5",
    152,
    1,
    mqtt_topic_suffix="timeofuse/time/5",
    unit="",
    signed=False,
    groups=["deye_sg01hp3_timeofuse"],
)

deye_sg01hp3_time_of_use_153 = SingleRegisterSensor(
    "Time of Use Time 6",
    153,
    1,
    mqtt_topic_suffix="timeofuse/time/6",
    unit="",
    signed=False,
    groups=["deye_sg01hp3_timeofuse"],
)

deye_sg01hp3_time_of_use_154 = SingleRegisterSensor(
    "Time of Use Power 1",
    154,
    10,
    mqtt_topic_suffix="timeofuse/power/1",
    unit="W",
    signed=False,
    groups=["deye_sg01hp3_timeofuse"],
)

deye_sg01hp3_time_of_use_155 = SingleRegisterSensor(
    "Time of Use Power 2",
    155,
    10,
    mqtt_topic_suffix="timeofuse/power/2",
    unit="W",
    signed=False,
    groups=["deye_sg01hp3_timeofuse"],
)

deye_sg01hp3_time_of_use_156 = SingleRegisterSensor(
    "Time of Use Power 3",
    156,
    10,
    mqtt_topic_suffix="timeofuse/power/3",
    unit="W",
    signed=False,
    groups=["deye_sg01hp3_timeofuse"],
)

deye_sg01hp3_time_of_use_157 = SingleRegisterSensor(
    "Time of Use Power 4",
    157,
    10,
    mqtt_topic_suffix="timeofuse/power/4",
    unit="W",
    signed=False,
    groups=["deye_sg01hp3_timeofuse"],
)

deye_sg01hp3_time_of_use_158 = SingleRegisterSensor(
    "Time of Use Power 5",
    158,
    10,
    mqtt_topic_suffix="timeofuse/power/5",
    unit="W",
    signed=False,
    groups=["deye_sg01hp3_timeofuse"],
)

deye_sg01hp3_time_of_use_159 = SingleRegisterSensor(
    "Time of Use Power 6",
    159,
    10,
    mqtt_topic_suffix="timeofuse/power/6",
    unit="W",
    signed=False,
    groups=["deye_sg01hp3_timeofuse"],
)

deye_sg01hp3_time_of_use_160 = SingleRegisterSensor(
    "Time of Use Voltage 1",
    160,
    0.1,
    mqtt_topic_suffix="timeofuse/voltage/1",
    unit="V",
    signed=False,
    groups=["deye_sg01hp3_timeofuse"],
)

deye_sg01hp3_time_of_use_161 = SingleRegisterSensor(
    "Time of Use Voltage 2",
    161,
    0.1,
    mqtt_topic_suffix="timeofuse/voltage/2",
    unit="V",
    signed=False,
    groups=["deye_sg01hp3_timeofuse"],
)

deye_sg01hp3_time_of_use_162 = SingleRegisterSensor(
    "Time of Use Voltage 3",
    162,
    0.1,
    mqtt_topic_suffix="timeofuse/voltage/3",
    unit="V",
    signed=False,
    groups=["deye_sg01hp3_timeofuse"],
)

deye_sg01hp3_time_of_use_163 = SingleRegisterSensor(
    "Time of Use Voltage 4",
    163,
    0.1,
    mqtt_topic_suffix="timeofuse/voltage/4",
    unit="V",
    signed=False,
    groups=["deye_sg01hp3_timeofuse"],
)

deye_sg01hp3_time_of_use_164 = SingleRegisterSensor(
    "Time of Use Voltage 5",
    164,
    0.1,
    mqtt_topic_suffix="timeofuse/voltage/5",
    unit="V",
    signed=False,
    groups=["deye_sg01hp3_timeofuse"],
)

deye_sg01hp3_time_of_use_165 = SingleRegisterSensor(
    "Time of Use Voltage 6",
    165,
    0.1,
    mqtt_topic_suffix="timeofuse/voltage/6",
    unit="V",
    signed=False,
    groups=["deye_sg01hp3_timeofuse"],
)

deye_sg01hp3_time_of_use_166 = SingleRegisterSensor(
    "Time of Use SOC 1",
    166,
    1,
    mqtt_topic_suffix="timeofuse/soc/1",
    unit="%",
    signed=False,
    groups=["deye_sg01hp3_timeofuse"],
)

deye_sg01hp3_time_of_use_167 = SingleRegisterSensor(
    "Time of Use SOC 2",
    167,
    1,
    mqtt_topic_suffix="timeofuse/soc/2",
    unit="%",
    signed=False,
    groups=["deye_sg01hp3_timeofuse"],
)

deye_sg01hp3_time_of_use_168 = SingleRegisterSensor(
    "Time of Use SOC 3",
    168,
    1,
    mqtt_topic_suffix="timeofuse/soc/3",
    unit="%",
    signed=False,
    groups=["deye_sg01hp3_timeofuse"],
)

deye_sg01hp3_time_of_use_169 = SingleRegisterSensor(
    "Time of Use SOC 4",
    169,
    1,
    mqtt_topic_suffix="timeofuse/soc/4",
    unit="%",
    signed=False,
    groups=["deye_sg01hp3_timeofuse"],
)

deye_sg01hp3_time_of_use_170 = SingleRegisterSensor(
    "Time of Use SOC 5",
    170,
    1,
    mqtt_topic_suffix="timeofuse/soc/5",
    unit="%",
    signed=False,
    groups=["deye_sg01hp3_timeofuse"],
)

deye_sg01hp3_time_of_use_171 = SingleRegisterSensor(
    "Time of Use SOC 6",
    171,
    1,
    mqtt_topic_suffix="timeofuse/soc/6",
    unit="%",
    signed=False,
    groups=["deye_sg01hp3_timeofuse"],
)

deye_sg01hp3_time_of_use_172 = SingleRegisterSensor(
    "Time of Use Charge Enable 1",
    172,
    1,
    mqtt_topic_suffix="timeofuse/enabled/1",
    unit="",
    signed=False,
    groups=["deye_sg01hp3_timeofuse"],
)

deye_sg01hp3_time_of_use_173 = SingleRegisterSensor(
    "Time of Use Charge Enable 2",
    173,
    1,
    mqtt_topic_suffix="timeofuse/enabled/2",
    unit="",
    signed=False,
    groups=["deye_sg01hp3_timeofuse"],
)

deye_sg01hp3_time_of_use_174 = SingleRegisterSensor(
    "Time of Use Charge Enable 3",
    174,
    1,
    mqtt_topic_suffix="timeofuse/enabled/3",
    unit="",
    signed=False,
    groups=["deye_sg01hp3_timeofuse"],
)

deye_sg01hp3_time_of_use_175 = SingleRegisterSensor(
    "Time of Use Charge Enable 4",
    175,
    1,
    mqtt_topic_suffix="timeofuse/enabled/4",
    unit="",
    signed=False,
    groups=["deye_sg01hp3_timeofuse"],
)

deye_sg01hp3_time_of_use_176 = SingleRegisterSensor(
    "Time of Use Charge Enable 5",
    176,
    1,
    mqtt_topic_suffix="timeofuse/enabled/5",
    unit="",
    signed=False,
    groups=["deye_sg01hp3_timeofuse"],
)

deye_sg01hp3_time_of_use_177 = SingleRegisterSensor(
    "Time of Use Charge Enable 6",
    177,
    1,
    mqtt_topic_suffix="timeofuse/enabled/6",
    unit="",
    signed=False,
    groups=["deye_sg01hp3_timeofuse"],
)


deye_sg01hp3_generator_661 = SingleRegisterSensor(
    "Phase voltage of Gen port L1",
    661,
    0.1,
    mqtt_topic_suffix="ac/generator/l1/voltage",
    unit="V",
    signed=False,
    groups=["deye_sg01hp3_generator"],
)

deye_sg01hp3_generator_662 = SingleRegisterSensor(
    "Phase voltage of Gen port L2",
    662,
    0.1,
    mqtt_topic_suffix="ac/generator/l2/voltage",
    unit="V",
    signed=False,
    groups=["deye_sg01hp3_generator"],
)

deye_sg01hp3_generator_663 = SingleRegisterSensor(
    "Phase voltage of Gen port L3",
    663,
    0.1,
    mqtt_topic_suffix="ac/generator/l3/voltage",
    unit="V",
    signed=False,
    groups=["deye_sg01hp3_generator"],
)

deye_sg01hp3_generator_664 = SingleRegisterSensor(
    "Phase power of Gen port L1",
    664,
    1,
    mqtt_topic_suffix="ac/generator/l1/power",
    unit="W",
    signed=True,
    groups=["deye_sg01hp3_generator"],
)

deye_sg01hp3_generator_665 = SingleRegisterSensor(
    "Phase power of Gen port L2",
    665,
    1,
    mqtt_topic_suffix="ac/generator/l2/power",
    unit="W",
    signed=True,
    groups=["deye_sg01hp3_generator"],
)

deye_sg01hp3_generator_666 = SingleRegisterSensor(
    "Phase power of Gen port L3",
    666,
    1,
    mqtt_topic_suffix="ac/generator/l3/power",
    unit="W",
    signed=True,
    groups=["deye_sg01hp3_generator"],
)

deye_sg01hp3_generator_667 = SingleRegisterSensor(
    "Total Power of Gen Ports",
    667,
    1,
    mqtt_topic_suffix="ac/generator/total_power",
    unit="W",
    signed=True,
    groups=["deye_sg01hp3_generator"],
)

deye_sg01hp3_generator_536 = SingleRegisterSensor(
    "Daily Generator Production",
    536,
    0.1,
    mqtt_topic_suffix="ac/generator/daily_energy",
    unit="kWh",
    signed=False,
    groups=["deye_sg01hp3_generator"],
)

deye_sg01hp3_generator_537 = SingleRegisterSensor(
    "Total Generator Production",
    537,
    0.1,
    mqtt_topic_suffix="ac/generator/total_energy",
    unit="kWh",
    signed=False,
    groups=["deye_sg01hp3_generator"],
)

deye_sg01hp3_sensors = [
    deye_sg01hp3_inverter_500,
    deye_sg01hp3_inverter_552,
    deye_sg01hp3_solar_672,
    deye_sg01hp3_solar_673,
    deye_sg01hp3_solar_674,
    deye_sg01hp3_solar_675,
    deye_sg01hp3_solar_676,
    deye_sg01hp3_solar_677,
    deye_sg01hp3_solar_678,
    deye_sg01hp3_solar_679,
    deye_sg01hp3_solar_680,
    deye_sg01hp3_solar_681,
    deye_sg01hp3_solar_682,
    deye_sg01hp3_solar_683,
    deye_sg01hp3_solar_529,
    deye_sg01hp3_solar_534,
    deye_sg01hp3_bms1_210,
    deye_sg01hp3_bms1_211,
    deye_sg01hp3_bms1_212,
    deye_sg01hp3_bms1_213,
    deye_sg01hp3_bms1_214,
    deye_sg01hp3_bms1_215,
    deye_sg01hp3_bms1_216,
    deye_sg01hp3_bms1_217,
    deye_sg01hp3_bms1_218,
    deye_sg01hp3_bms1_219,
    deye_sg01hp3_bms2_241,
    deye_sg01hp3_bms2_242,
    deye_sg01hp3_bms2_243,
    deye_sg01hp3_bms2_244,
    deye_sg01hp3_bms2_245,
    deye_sg01hp3_bms2_246,
    deye_sg01hp3_bms2_247,
    deye_sg01hp3_bms2_248,
    deye_sg01hp3_bms2_249,
    deye_sg01hp3_bms2_250,
    deye_sg01hp3_battery_514,
    deye_sg01hp3_battery_515,
    deye_sg01hp3_battery_516,
    deye_sg01hp3_battery_518,
    deye_sg01hp3_battery1_590,
    deye_sg01hp3_battery1_587,
    deye_sg01hp3_battery1_588,
    deye_sg01hp3_battery1_591,
    deye_sg01hp3_battery1_586,
    deye_sg01hp3_battery2_589,
    deye_sg01hp3_battery2_593,
    deye_sg01hp3_battery2_594,
    deye_sg01hp3_battery2_595,
    deye_sg01hp3_battery2_596,
    deye_sg01hp3_grid_625,
    deye_sg01hp3_grid_598,
    deye_sg01hp3_grid_599,
    deye_sg01hp3_grid_600,
    deye_sg01hp3_grid_604,
    deye_sg01hp3_grid_605,
    deye_sg01hp3_grid_606,
    deye_sg01hp3_grid_616,
    deye_sg01hp3_grid_617,
    deye_sg01hp3_grid_618,
    deye_sg01hp3_grid_520,
    deye_sg01hp3_grid_522,
    deye_sg01hp3_grid_521,
    deye_sg01hp3_grid_524,
    ongrid_status_sensor,
    deye_sg01hp3_upload_653,
    deye_sg01hp3_upload_650,
    deye_sg01hp3_upload_651,
    deye_sg01hp3_upload_652,
    deye_sg01hp3_upload_644,
    deye_sg01hp3_upload_645,
    deye_sg01hp3_upload_646,
    deye_sg01hp3_upload_526,
    deye_sg01hp3_upload_527,
    deye_sg01hp3_inverter_630,
    deye_sg01hp3_inverter_631,
    deye_sg01hp3_inverter_632,
    deye_sg01hp3_inverter_633,
    deye_sg01hp3_inverter_634,
    deye_sg01hp3_inverter_635,
    deye_sg01hp3_inverter_540,
    deye_sg01hp3_inverter_541,
    total_pv_power_sensor,
    deye_sg01hp3_time_of_use_146,
    deye_sg01hp3_time_of_use_148,
    deye_sg01hp3_time_of_use_149,
    deye_sg01hp3_time_of_use_150,
    deye_sg01hp3_time_of_use_151,
    deye_sg01hp3_time_of_use_152,
    deye_sg01hp3_time_of_use_153,
    deye_sg01hp3_time_of_use_154,
    deye_sg01hp3_time_of_use_155,
    deye_sg01hp3_time_of_use_156,
    deye_sg01hp3_time_of_use_157,
    deye_sg01hp3_time_of_use_158,
    deye_sg01hp3_time_of_use_159,
    deye_sg01hp3_time_of_use_160,
    deye_sg01hp3_time_of_use_161,
    deye_sg01hp3_time_of_use_162,
    deye_sg01hp3_time_of_use_163,
    deye_sg01hp3_time_of_use_164,
    deye_sg01hp3_time_of_use_165,
    deye_sg01hp3_time_of_use_166,
    deye_sg01hp3_time_of_use_167,
    deye_sg01hp3_time_of_use_168,
    deye_sg01hp3_time_of_use_169,
    deye_sg01hp3_time_of_use_170,
    deye_sg01hp3_time_of_use_171,
    deye_sg01hp3_time_of_use_172,
    deye_sg01hp3_time_of_use_173,
    deye_sg01hp3_time_of_use_174,
    deye_sg01hp3_time_of_use_175,
    deye_sg01hp3_time_of_use_176,
    deye_sg01hp3_time_of_use_177,
    deye_sg01hp3_generator_661,
    deye_sg01hp3_generator_662,
    deye_sg01hp3_generator_663,
    deye_sg01hp3_generator_664,
    deye_sg01hp3_generator_665,
    deye_sg01hp3_generator_666,
    deye_sg01hp3_generator_667,
    deye_sg01hp3_generator_536,
    deye_sg01hp3_generator_537,
]

deye_sg01hp3_register_ranges = [
    SensorRegisterRange(group="deye_sg01hp3", first_reg_address=500, last_reg_address=500),
    SensorRegisterRange(group="deye_sg01hp3", first_reg_address=552, last_reg_address=552),
    SensorRegisterRange(group="deye_sg01hp3_ups", first_reg_address=514, last_reg_address=558),
    SensorRegisterRange(group="deye_sg01hp3", first_reg_address=514, last_reg_address=558),
    SensorRegisterRange(group="deye_sg01hp3_battery", first_reg_address=514, last_reg_address=558),
    SensorRegisterRange(group="deye_sg01hp3_battery", first_reg_address=586, last_reg_address=596),
    SensorRegisterRange(group="deye_sg01hp3", first_reg_address=598, last_reg_address=636),
    SensorRegisterRange(group="deye_sg01hp3_ups", first_reg_address=644, last_reg_address=653),
    SensorRegisterRange(group="deye_sg01hp3", first_reg_address=672, last_reg_address=683),
    SensorRegisterRange(group="deye_sg01hp3_bms", first_reg_address=210, last_reg_address=219),
    SensorRegisterRange(group="deye_sg01hp3_bms", first_reg_address=241, last_reg_address=250),
    SensorRegisterRange(group="deye_sg01hp3_timeofuse", first_reg_address=146, last_reg_address=177),
    SensorRegisterRange(group="deye_sg01hp3_generator", first_reg_address=661, last_reg_address=667),
    SensorRegisterRange(group="deye_sg01hp3_generator", first_reg_address=536, last_reg_address=537),
]
