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

from abc import abstractmethod


class Sensor:
    """
    Models solar inverter sensor.

    This is an abstract class. Method 'read_value' must be provided by the extending subclass.
    """

    def __init__(self, name: str, mqtt_topic_suffix="", unit="", print_format="{:s}", groups=[]):
        self.name = name
        self.mqtt_topic_suffix = mqtt_topic_suffix
        self.unit = unit
        self.print_format = print_format
        assert len(groups) > 0, f"Sensor {name} must belong to at least one group"
        self.groups = groups

    @abstractmethod
    def read_value(self, registers: dict[int, bytearray]):
        """
        Reads sensor value from Modbus registers
        """
        pass

    def write_value(self, value: str) -> dict[int, bytearray]:
        """
        Converts value into bytes representation.
        Useful for configuration modifications, when values are written to the inverter.
        """
        return {}

    def format_value(self, value):
        """
        Formats sensor value using configured format string
        """
        return self.print_format.format(value)

    def in_any_group(self, active_groups: set[str]) -> bool:
        """
        Checks if this sensor is included in at least one of the given active_groups.
        Sensor matches any group when its groups set is empty (default behavior)
        """
        return not self.groups or len(active_groups.intersection(self.groups)) > 0

    @abstractmethod
    def get_registers(self) -> list[int]:
        """Returns the list of Modbus registers read by this sensor"""


class SingleRegisterSensor(Sensor):
    """
    Solar inverter sensor with value stored as 32-bit integer in a single Modbus register.
    """

    def __init__(
        self,
        name: str,
        reg_address: int,
        factor: float,
        offset: float = 0,
        signed=False,
        mqtt_topic_suffix="",
        unit="",
        print_format="{:0.1f}",
        groups=[],
    ):
        super().__init__(name, mqtt_topic_suffix, unit, print_format, groups)
        self.reg_address = reg_address
        self.factor = factor
        self.offset = offset
        self.signed = signed

    def read_value(self, registers: dict[int, bytearray]):
        if self.reg_address in registers:
            reg_value = registers[self.reg_address]
            return int.from_bytes(reg_value, "big", signed=self.signed) * self.factor + self.offset
        else:
            return None

    def write_value(self, value: str) -> dict[int, bytearray]:
        return {self.reg_address: int(value).to_bytes(2, "big", signed=self.signed)}

    @abstractmethod
    def get_registers(self) -> list[int]:
        return [self.reg_address]


class DoubleRegisterSensor(Sensor):
    """
    Solar inverter sensor with value stored as 64-bit integer in two Modbus registers.
    """

    def __init__(
        self,
        name: str,
        reg_address: int,
        factor: float,
        offset: float = 0,
        signed=False,
        mqtt_topic_suffix="",
        unit="",
        print_format="{:0.1f}",
        groups=[],
    ):
        super().__init__(name, mqtt_topic_suffix, unit, print_format, groups)
        self.reg_address = reg_address
        self.factor = factor
        self.offset = offset
        self.signed = signed

    def read_value(self, registers: dict[int, bytearray]):
        low_word_reg_address = self.reg_address
        high_word_reg_address = self.reg_address + 1
        if low_word_reg_address in registers and high_word_reg_address in registers:
            low_word = registers[low_word_reg_address]
            high_word = registers[high_word_reg_address]
            return int.from_bytes(high_word + low_word, "big", signed=self.signed) * self.factor + self.offset
        else:
            return None

    @abstractmethod
    def get_registers(self) -> list[int]:
        return [self.reg_address, self.reg_address + 1]


class SignedMagnitudeSingleRegisterSensor(SingleRegisterSensor):
    """
    Reads single Modbus register as signed, fixed point 15-bits long value.
    The most significant bit encodes the sign.
    """

    def read_value(self, registers: dict[int, bytearray]):
        if self.reg_address in registers:
            reg_value = int.from_bytes(registers[self.reg_address], "big", signed=False) & 0x7FFF
            # If highest bit is set, we've got a negative value
            if bool(registers[self.reg_address][0] & 0x80):
                return -1 * reg_value * self.factor + self.offset
            else:
                return reg_value * self.factor + self.offset
        else:
            return None


class SignedMagnitudeDoubleRegisterSensor(DoubleRegisterSensor):
    """
    Reads double Modbus registers as signed, fixed point 31-bits long value.
    The most significant bit encodes the sign.
    """

    def read_value(self, registers: dict[int, bytearray]):
        high_word_reg_address = self.reg_address
        low_word_reg_address = self.reg_address + 1
        if low_word_reg_address in registers and high_word_reg_address in registers:
            low_word = registers[low_word_reg_address]
            high_word = registers[high_word_reg_address]
            reg_value = int.from_bytes(high_word + low_word, "big", signed=False) & 0x7FFFFFFF
            # If highest bit is set, we've got a negative value
            if bool(registers[self.reg_address][0] & 0x80):
                return -1 * reg_value * self.factor + self.offset
            else:
                return reg_value * self.factor + self.offset
        else:
            return None


class ComputedPowerSensor(Sensor):
    """
    Electric Power sensor with value computed as multiplication of values read by voltage and current sensors.
    """

    def __init__(
        self,
        name: str,
        voltage_sensor: Sensor,
        current_sensor: Sensor,
        mqtt_topic_suffix="",
        unit="",
        print_format="{:0.1f}",
        groups=[],
    ):
        super().__init__(name, mqtt_topic_suffix, unit, print_format, groups)
        self.voltage_sensor = voltage_sensor
        self.current_sensor = current_sensor

    def read_value(self, registers: dict[int, bytearray]):
        voltage = self.voltage_sensor.read_value(registers)
        current = self.current_sensor.read_value(registers)
        if voltage is not None and current is not None:
            return voltage * current
        else:
            return None

    @abstractmethod
    def get_registers(self) -> list[int]:
        return []


class ComputedSumSensor(Sensor):
    """
    Computes a sum of values read by given list of sensors.
    """

    def __init__(
        self, name: str, sensors: list[Sensor], mqtt_topic_suffix="", unit="", print_format="{:0.1f}", groups=[]
    ):
        super().__init__(name, mqtt_topic_suffix, unit, print_format, groups)
        self.sensors = sensors

    def read_value(self, registers: dict[int, bytearray]):
        result = 0
        sensor_values = [s.read_value(registers) for s in self.sensors]
        for value in sensor_values:
            if value is None:
                return None
            result += value
        return result

    @abstractmethod
    def get_registers(self) -> list[int]:
        return []


class SensorRegisterRange:
    """
    Declares a Modbus register range that must be read to provide values for sensors within a metrics group
    """

    def __init__(self, group: str, first_reg_address: int, last_reg_address: int):
        self.group = group
        self.first_reg_address = first_reg_address
        self.last_reg_address = last_reg_address

    def in_any_group(self, active_groups: set[str]) -> bool:
        """
        Checks if this range is included in at least one of the given active_groups.
        """
        return self.group in active_groups

    def is_same_range(self, other: "SensorRegisterRange") -> bool:
        """Checks if the other range has this same first and last reg address.

        Args:
            other (SensorRegisterRange): to check against

        Returns:
            bool: True when both ranges define this same registers addresses, False otherwise
        """
        return self.first_reg_address == other.first_reg_address and self.last_reg_address == other.last_reg_address

    def __str__(self):
        return "metrics group: {}, range: {:04x}-{:04x}".format(
            self.group, self.first_reg_address, self.last_reg_address
        )
