import sys
sys.path.append('..')

import argparse
from deye_sensors import sensor_list
from deye_sensor import Sensor


def render_table(sensors: list[Sensor]):
    for s in sensors:
        regs = ','.join(['{:d}'.format(r) for r in s.get_registers()])
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