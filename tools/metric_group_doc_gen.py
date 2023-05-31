import sys
sys.path.append('../src')

from deye_sensor import Sensor
from deye_sensors import sensor_list
import argparse

def render_table(sensors: list[Sensor]):
    print('|Metric|Modbus address|MQTT topic suffix|Unit|')
    print('|---|:-:|---|:-:|')
    for s in sensors:
        regs = ','.join(['{:d}'.format(r) for r in s.get_registers()])
        if not regs:
            regs = 'computed'
        print(f"|{s.name}|{regs}|`{s.mqtt_topic_suffix}`|{s.unit}|")


def main():
    parser = argparse.ArgumentParser(description='Documentation generator')
    parser.add_argument('--group-name', type=str, help='metrics group name')
    args = parser.parse_args()
    group_name = args.group_name

    sensors_in_group = [s for s in sensor_list if s.in_any_group({group_name})]

    render_table(sensors_in_group)


if __name__ == "__main__":
    main()
