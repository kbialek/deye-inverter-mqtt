import os
import yaml
from yaml.loader import SafeLoader

import argparse
from typing import IO


class SensorDef:
    def __init__(self, name: str, group: str, code: str, reg_min: int, reg_max: int):
        self.name = name
        self.group = group
        self.code = code
        self.reg_min = reg_min
        self.reg_max = reg_max


class RegisterRangeDef:
    def __init__(self, reg_min: int, reg_max: int):
        self.reg_min = reg_min
        self.reg_max = reg_max

    def get_code(self, group_name: str) -> str:
        return f"SensorRegisterRange(group='{group_name}', first_reg_address={self.reg_min}, last_reg_address={self.reg_max})"

    def contains(self, reg: int) -> bool:
        return reg >= self.reg_min and reg <= self.reg_max

    def combine(self, other: 'RegisterRangeDef') -> 'RegisterRangeDef':
        min = None
        max = None
        if other.reg_min < self.reg_min and other.reg_max >= self.reg_min:
            min = other.reg_min
        if other.reg_max > self.reg_max and other.reg_min <= self.reg_max:
            max = other.reg_max
        if other.reg_min >= self.reg_min and other.reg_max <= self.reg_max:
            min = self.reg_min
            max = self.reg_max
        if other.reg_min <= self.reg_min and other.reg_max >= self.reg_max:
            min = other.reg_min
            max = other.reg_max
        if min and max:
            return RegisterRangeDef(min, max)
        else:
            return None


def import_single_register_item(group_prefix: str, group_name: str, parameter_item: dict, map: dict, signed: bool) -> SensorDef:
    name = parameter_item['name']
    register = parameter_item['registers'][0]
    topics = map['topics']
    groups_map = map['groups']
    if register not in topics or group_name not in groups_map:
        return None
    scale = parameter_item['scale']
    offset = parameter_item['offset'] if 'offset' in parameter_item else None
    gn = group_name.replace(' ', '_')
    sensor_name = f'{group_prefix}_{gn}_{register}'
    group_suffix = groups_map[group_name]
    if group_suffix:
        group_suffix = '_' + group_suffix
    sensor_group_name = group_prefix + group_suffix
    topic = topics[register]
    fill = ' ' * len(sensor_name)
    offset_code = f" offset={-offset/10}," if offset else ''
    unit = parameter_item['uom']
    code = f"""{sensor_name} = SingleRegisterSensor('{name}', {register}, {scale},{offset_code}
           {fill}             mqtt_topic_suffix='{topic}', unit='{unit}', signed={signed},
           {fill}             groups=['{sensor_group_name}'])\n\n"""
    return SensorDef(sensor_name, sensor_group_name, code, register, register)


def import_double_register_item(group_prefix: str, group_name: str, parameter_item: dict, map: dict, signed: bool) -> SensorDef:
    name = parameter_item['name']
    reg_min = parameter_item['registers'][0]
    reg_max = parameter_item['registers'][1]
    topics = map['topics']
    groups_map = map['groups']
    if reg_min not in topics or group_name not in groups_map:
        return None
    scale = parameter_item['scale']
    offset = parameter_item['offset'] if 'offset' in parameter_item else None
    sensor_name = f'{group_prefix}_{group_name}_{reg_min}'
    group_suffix = groups_map[group_name]
    if group_suffix:
        group_suffix = '_' + group_suffix
    sensor_group_name = group_prefix + group_suffix
    topic = topics[reg_min]
    fill = ' ' * len(sensor_name)
    offset_code = f" offset={-offset/10}," if offset else ''
    unit = parameter_item['uom']
    code = f"""{sensor_name} = DoubleRegisterSensor('{name}', {reg_min}, {scale},{offset_code}
           {fill}             mqtt_topic_suffix='{topic}', unit='{unit}', signed={signed},
           {fill}             groups=['{sensor_group_name}'])\n\n"""
    return SensorDef(sensor_name, sensor_group_name, code, reg_min, reg_max)


def import_parameter_item(group_prefix: str, group_name: str, parameter_item: dict, topics_map: dict) -> SensorDef:
    registers_count = len(parameter_item['registers'])
    rule = parameter_item['rule']
    if registers_count == 1:
        return import_single_register_item(group_prefix, group_name, parameter_item, topics_map, rule == 2)
    elif registers_count == 2:
        return import_double_register_item(group_prefix, group_name, parameter_item, topics_map, rule == 4)
    else:
        print(f'Unsupported register count {registers_count}')
        return None


def import_parameter_group(group_prefix: str, parameter_group: dict, topics_map: dict) -> list[SensorDef]:
    group_name = parameter_group['group'].lower()
    group_items = parameter_group['items']
    sensors = []
    for item in group_items:
        sensor = import_parameter_item(group_prefix, group_name, item, topics_map)
        if sensor:
            sensors.append(sensor)
    return sensors


def render_sensors_file(
        group_prefix: str, sensors_file: IO, sensors: list[SensorDef],
        register_ranges: list[RegisterRangeDef]):
    script_dir = os.path.dirname(__file__)
    with open(f'{script_dir}/sensors_file_header.py', mode='r', encoding='utf8') as header_file:
        sensors_file.writelines(header_file.readlines())

    groups = set()
    sensors_names = []
    regs_to_read_for_group = {}
    for sensor in sensors:
        sensors_file.write(sensor.code)
        sensors_names.append(sensor.name)
        groups.add(sensor.group)
        regs_to_read = regs_to_read_for_group.get(sensor.group, set())
        regs_to_read.add(sensor.reg_min)
        regs_to_read.add(sensor.reg_max)
        regs_to_read_for_group[sensor.group] = regs_to_read

    ranges_code = []
    for register_range in register_ranges:
        for group_name in groups:
            regs_to_read = regs_to_read_for_group[group_name]
            if [reg for reg in regs_to_read if register_range.contains(reg)]:
                ranges_code.append(register_range.get_code(group_name))

    delimiter = ',\n    '

    sensors_file.write(f'{group_prefix}_sensors = [\n    {delimiter.join(sensors_names)}')
    sensors_file.write('\n]\n\n')

    sensors_file.write(f'{group_prefix}_register_ranges = [\n    {delimiter.join(ranges_code)}')
    sensors_file.write('\n]\n\n')

def add_register_range(ranges: list[RegisterRangeDef], range_to_add: RegisterRangeDef) -> list[RegisterRangeDef]:
    new_ranges: list[RegisterRangeDef] = []
    combinded = False
    for rr in ranges:
        combined_range = rr.combine(range_to_add)
        if combined_range:
            new_ranges.append(combined_range)
            combinded = True
        else:
            new_ranges.append(rr)
    if not combinded:
        new_ranges.append(range_to_add)
    return new_ranges

def main():
    parser = argparse.ArgumentParser(description='Home Assistant inverter definition importer')
    parser.add_argument('--definition-code', type=str, help='metrics group prefix')
    parser.add_argument('--sensors-file', type=str, help='generated sensors file location')
    args = parser.parse_args()
    definition_code = args.definition_code
    sensors_file_path = args.sensors_file

    sensors = []
    register_ranges = []
    custom_definition_file_path = f'{definition_code}_ha_custom.yaml'
    map = {}
    data = {}
    custom_data = {}
    
    with open(f'{definition_code}_ha.yaml', mode='r', encoding='utf8') as definition_file:
        data = yaml.load(definition_file, Loader=SafeLoader)
    
    with open(f'{definition_code}_map.yaml') as map_file:
        map = yaml.load(map_file, Loader=SafeLoader)
    
    if os.path.exists(custom_definition_file_path):
        with open(custom_definition_file_path, mode='r', encoding='utf8') as custom_definition_file:
            custom_data = yaml.load(custom_definition_file, Loader=SafeLoader)
        
    parameter_groups: list = data['parameters'] + custom_data.get('parameters', [])
    for parameter_group in parameter_groups:
        for sensor in import_parameter_group(definition_code, parameter_group, map):
            if not [s for s in sensors if sensor.reg_min == s.reg_min]:
                sensors.append(sensor) 
    requests = data['requests'] + custom_data.get('requests', [])
    for request in requests:
        register_ranges = add_register_range(register_ranges, RegisterRangeDef(request['start'], request['end']))

    with open(sensors_file_path, mode='w', encoding='utf8') as sensors_file:
        render_sensors_file(definition_code, sensors_file, sensors, register_ranges)


if __name__ == "__main__":
    main()
