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
    SensorRegisterRange,
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


deye_sg01hp3_sensors = [
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
]

deye_sg01hp3_register_ranges = [
    SensorRegisterRange(group="deye_sg01hp3_ups", first_reg_address=514, last_reg_address=558),
    SensorRegisterRange(group="deye_sg01hp3", first_reg_address=514, last_reg_address=558),
    SensorRegisterRange(group="deye_sg01hp3_battery", first_reg_address=514, last_reg_address=558),
    SensorRegisterRange(group="deye_sg01hp3_battery", first_reg_address=586, last_reg_address=596),
    SensorRegisterRange(group="deye_sg01hp3", first_reg_address=598, last_reg_address=636),
    SensorRegisterRange(group="deye_sg01hp3_ups", first_reg_address=644, last_reg_address=653),
    SensorRegisterRange(group="deye_sg01hp3", first_reg_address=672, last_reg_address=683),
    SensorRegisterRange(group="deye_sg01hp3_bms", first_reg_address=210, last_reg_address=219),
    SensorRegisterRange(group="deye_sg01hp3_bms", first_reg_address=241, last_reg_address=250),
]
