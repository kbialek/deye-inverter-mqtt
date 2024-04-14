import sys
sys.path.append('../src')

from deye_sensor import Sensor, SingleRegisterSensor, SignedMagnitudeSingleRegisterSensor, DoubleRegisterSensor, SignedMagnitudeDoubleRegisterSensor
from deye_sensors import sensor_list
import argparse

def render_table(sensors: list[Sensor]):
    print('|Metric|MQTT topic suffix|Unit|Modbus address (dec)|Modbus address (hex)|Modbus data type|Scale factor|')
    print('|---|---|:-:|:-:|:-:|:-:|:-:|')
    for s in sensors:
        data_type = 'n/a'
        scale_factor = '1'
        if isinstance(s, SignedMagnitudeSingleRegisterSensor):
            data_type = 'SM_WORD'
            scale_factor = s.factor
        elif isinstance(s, SingleRegisterSensor):
            data_type = 'S_WORD' if s.signed else 'U_WORD'
            scale_factor = s.factor
        elif isinstance(s, SignedMagnitudeDoubleRegisterSensor):
            data_type = 'SM_DWORD'
            data_type += ' (LW,HW)' if s.low_word_first else ' (HW,LW)'
            scale_factor = s.factor
        elif isinstance(s, DoubleRegisterSensor):
            data_type = 'S_DWORD' if s.signed else 'U_DWORD'
            data_type += ' (LW,HW)' if s.low_word_first else ' (HW,LW)'
            scale_factor = s.factor

        regs_dec = ','.join(['{:d}'.format(r) for r in s.get_registers()])
        regs_hex = ','.join(['{:x}'.format(r) for r in s.get_registers()])
        if not regs_dec:
            regs_dec = 'computed'
        if not regs_hex:
            regs_hex = 'computed'

        print(f"|{s.name}|`{s.mqtt_topic_suffix}`|{s.unit}|{regs_dec}|{regs_hex}|{data_type}|{scale_factor}|")


def main():
    parser = argparse.ArgumentParser(description='Documentation generator')
    parser.add_argument('--group-name', type=str, help='metrics group name')
    args = parser.parse_args()
    group_name = args.group_name

    sensors_in_group = [s for s in sensor_list if s.in_any_group({group_name})]

    render_table(sensors_in_group)


if __name__ == "__main__":
    main()
