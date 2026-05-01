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

import pytest
from datetime import datetime
from deye_sensor import (
    Sensor,
    AbstractSensor,
    ComputedSumSensor,
    DoubleRegisterSensor,
    SingleRegisterSensor,
    SignedMagnitudeSingleRegisterSensor,
    SignedMagnitudeDoubleRegisterSensor,
    SensorRegisterRange,
    SensorRegisterRanges,
    ComputedBooleanSensor,
    DateTimeSensor,
)


class FakeSensor(AbstractSensor):
    def __init__(self, name, value):
        super().__init__(name, groups=["string"])
        self.value = value

    def read_value(self, registers):
        return self.value

    def get_registers(self) -> list[int]:
        return []


class TestDeyeSensor:
    def test_sum_sensor_returns_sum_when_all_inputs_are_given(self):
        # given
        test_sensor1 = FakeSensor("ts1", 1.1)
        test_sensor2 = FakeSensor("ts2", 2.2)

        # and
        sut = ComputedSumSensor("sum", [test_sensor1, test_sensor2], groups=["string"])

        # when
        result = sut.read_value([])

        # then
        assert result == pytest.approx(3.3)

    def test_sum_sensor_returns_none_when_any_input_is_none(self):
        # given
        test_sensor1 = FakeSensor("ts1", 1.1)
        test_sensor2 = FakeSensor("ts2", None)

        # and
        sut = ComputedSumSensor("sum", [test_sensor1, test_sensor2], groups=["string"])

        # when
        result = sut.read_value([])

        # then
        assert result is None

    def test_single_reg_sensor_unsigned(self):
        # given
        sut = SingleRegisterSensor("test", 0x00, 1, signed=False, groups=["string"])

        # and
        registers = {0: bytearray.fromhex("0102")}

        # when
        result = sut.read_value(registers)

        # then
        assert result == 0x0102

    def test_single_reg_sensor_signed(self):
        # given
        sut = SingleRegisterSensor("test", 0x00, 1, signed=True, groups=["string"])

        # and
        registers = {0: bytearray.fromhex("fffe")}

        # when
        result = sut.read_value(registers)

        # then
        assert result == -2

    def test_double_reg_sensor_unsigned(self):
        # given
        sut = DoubleRegisterSensor("test", 0x00, 1, signed=False, groups=["string"])

        # and
        registers = {0: bytearray.fromhex("0102"), 1: bytearray.fromhex("0304")}  # low word  # high word

        # when
        result = sut.read_value(registers)

        # then
        assert result == 0x03040102

    def test_double_reg_sensor_signed(self):
        # given
        sut = DoubleRegisterSensor("test", 0x00, 1, signed=True, groups=["string"])

        # and
        registers = {0: bytearray.fromhex("fffe"), 1: bytearray.fromhex("ffff")}  # low word  # high word

        # when
        result = sut.read_value(registers)

        # then
        assert result == -2

    def test_double_reg_sensor_unsigned_high_word_first(self):
        # given
        sut = DoubleRegisterSensor("test", 0x00, 1, signed=False, groups=["string"], low_word_first=False)

        # and
        registers = {0: bytearray.fromhex("0102"), 1: bytearray.fromhex("0304")}  # low word  # high word

        # when
        result = sut.read_value(registers)

        # then
        assert result == 0x01020304

    def test_signed_magnitude_single_register_signed(self):
        # given
        sut = SignedMagnitudeSingleRegisterSensor("test", 0x00, 1, groups=["igen_dtsd422"])

        # and
        registers = {0: bytearray.fromhex("8310")}

        # when
        result = sut.read_value(registers)

        # then
        assert result == -784

    def test_signed_magnitude_single_register_unsigned(self):
        # given
        sut = SignedMagnitudeSingleRegisterSensor("test", 0x00, 1, groups=["igen_dtsd422"])

        # and
        registers = {0: bytearray.fromhex("0310")}

        # when
        result = sut.read_value(registers)

        # then
        assert result == 784

    def test_signed_magnitude_double_register_signed(self):
        # given
        sut = SignedMagnitudeDoubleRegisterSensor("test", 0x00, 1, groups=["igen_dtsd422"])

        # and
        registers = {0: bytearray.fromhex("8000"), 1: bytearray.fromhex("0101")}  # high word  # low word

        # when
        result = sut.read_value(registers)

        # then
        assert result == -257

    def test_signed_magnitude_double_register_unsigned(self):
        # given
        sut = SignedMagnitudeDoubleRegisterSensor("test", 0x00, 1, groups=["igen_dtsd422"])

        # and
        registers = {0: bytearray.fromhex("0000"), 1: bytearray.fromhex("0101")}  # high word  # low word

        # when
        result = sut.read_value(registers)

        # then
        assert result == 257

    def test_single_reg_sensor_write_unsigned(self):
        # given
        sut = SingleRegisterSensor("test", 0x00, 1, signed=False, groups=["string"])

        # when
        result = sut.write_value("1234")

        # then
        assert result == {0: bytearray.fromhex("04d2")}

    def test_single_reg_sensor_write_signed(self):
        # given
        sut = SingleRegisterSensor("test", 0x00, 1, signed=True, groups=["string"])

        # when
        result = sut.write_value("-1234")

        # then
        assert result == {0: bytearray.fromhex("fb2e")}

    def test_split_long_register_range(self):
        # given
        sut = SensorRegisterRange("test", 10, 50)

        # when
        result = sut.split(21)

        # then
        assert len(result) == 2
        assert result[0].length == 21
        assert result[0].first_reg_address == 10
        assert result[0].last_reg_address == 30
        assert result[1].length == 20
        assert result[1].first_reg_address == 31
        assert result[1].last_reg_address == 50

    def test_split_short_register_range(self):
        # given
        sut = SensorRegisterRange("test", 10, 50)

        # when
        result = sut.split(45)

        # then
        assert len(result) == 1
        assert result[0].length == 41
        assert result[0].first_reg_address == 10
        assert result[0].last_reg_address == 50

    def test_prep_register_ranges(self):
        # when
        sut = SensorRegisterRanges(
            ranges=[
                SensorRegisterRange("a", 1, 10),
                SensorRegisterRange("b", 20, 40),
                SensorRegisterRange("c", 60, 70),
                SensorRegisterRange("d", 100, 102),
            ],
            metric_groups=["a", "b", "c"],
            max_range_length=15,
        )

        # then
        assert len(sut.ranges) == 4
        assert sut.ranges[0].group == {"a"}
        assert sut.ranges[0].first_reg_address == 1
        assert sut.ranges[0].last_reg_address == 10
        assert sut.ranges[1].group == {"b"}
        assert sut.ranges[1].first_reg_address == 20
        assert sut.ranges[1].last_reg_address == 34
        assert sut.ranges[2].group == {"b"}
        assert sut.ranges[2].first_reg_address == 35
        assert sut.ranges[2].last_reg_address == 40
        assert sut.ranges[3].group == {"c"}
        assert sut.ranges[3].first_reg_address == 60
        assert sut.ranges[3].last_reg_address == 70

    def test_registry_range_single_group_name(self):
        # given
        sut = SensorRegisterRange("a", 1, 2)

        # expect
        assert sut.in_any_group({"a"}) is True
        assert sut.in_any_group({"b"}) is False

    def test_registry_range_multiple_groups_names(self):
        # given
        sut = SensorRegisterRange({"a", "b"}, 1, 2)

        # expect
        assert sut.in_any_group({"a"}) is True
        assert sut.in_any_group({"b"}) is True
        assert sut.in_any_group({"c"}) is False

    def test_reset_sensor_passthrough(self):
        # given
        sut = SingleRegisterSensor("test", 0x00, 1, signed=False, groups=["string"]).reset_daily()

        # and
        registers = {0: bytearray.fromhex("0102")}

        # when
        result = sut.read_value(registers)

        # then
        assert result == 0x0102

    def test_boolean_sensor_returns_true_when_mask_matches(self):
        # given
        test_sensor1 = FakeSensor("ts1", 0xAA)
        test_sensor2 = FakeSensor("ts2", 0x55)

        # and
        sut1 = ComputedBooleanSensor(
            "test1",
            bitarray_sensor=test_sensor1,
            mask=1,
            groups=["string"],
        )
        sut2 = ComputedBooleanSensor(
            "test2",
            bitarray_sensor=test_sensor1,
            mask=0xFF,
            groups=["string"],
        )
        sut3 = ComputedBooleanSensor(
            "test3",
            bitarray_sensor=test_sensor1,
            mask=0xAA,
            groups=["string"],
        )
        sut4 = ComputedBooleanSensor(
            "test4",
            bitarray_sensor=test_sensor1,
            mask=0x55,
            groups=["string"],
        )
        sut5 = ComputedBooleanSensor(
            "test5",
            bitarray_sensor=test_sensor2,
            mask=1,
            groups=["string"],
        )
        sut6 = ComputedBooleanSensor(
            "test6",
            bitarray_sensor=test_sensor2,
            mask=0xFF,
            groups=["string"],
        )
        sut7 = ComputedBooleanSensor(
            "test7",
            bitarray_sensor=test_sensor2,
            mask=0xAA,
            groups=["string"],
        )
        sut8 = ComputedBooleanSensor(
            "test8",
            bitarray_sensor=test_sensor2,
            mask=0x55,
            groups=["string"],
        )

        # when
        result1 = sut1.read_value([])
        result2 = sut2.read_value([])
        result3 = sut3.read_value([])
        result4 = sut4.read_value([])
        result5 = sut5.read_value([])
        result6 = sut6.read_value([])
        result7 = sut7.read_value([])
        result8 = sut8.read_value([])

        # then
        assert result1 is False
        assert result2 is False
        assert result3 is True
        assert result4 is False
        assert result5 is True
        assert result6 is False
        assert result7 is False
        assert result8 is True

    def test_datetime_sensor(self):
        # given
        sut = DateTimeSensor(
            "test",
            22,
            mqtt_topic_suffix="settings/system_time",
            groups=["test"],
        )

        # and
        now = datetime.now().replace(microsecond=0)

        # and
        reg0_value = (256 * (now.year % 100) + now.month).to_bytes(2, "big", signed=False)
        reg1_value = (256 * now.day + now.hour).to_bytes(2, "big", signed=False)
        reg2_value = (256 * now.minute + now.second).to_bytes(2, "big", signed=False)
        registers = {22: reg0_value, 23: reg1_value, 24: reg2_value}

        # when
        result1 = sut.read_value(registers)
        result2 = sut.write_value(now)

        # then
        assert result1 == now.timestamp()
        assert result2 == {22: [reg0_value, reg1_value, reg2_value]}

    def test_datetime_sensor_wrong_input(self):
        # given
        sut = DateTimeSensor(
            "test",
            22,
            mqtt_topic_suffix="settings/system_time",
            groups=["test"],
        )

        # and
        registers = {22: bytes([0x00]), 23: bytes([0x00]), 24: bytes([0x00])}

        # when
        result = sut.read_value(registers)

        # then
        assert result is None

    def test_format_value_uses_custom_print_format(self):
        # given
        sut = SingleRegisterSensor("test", 0x00, 1.0, signed=False, print_format="{:d}", groups=["string"])

        # when
        result = sut.format_value(42)

        # then
        assert result == "42"

    def test_format_value_default_format(self):
        # given
        sut = SingleRegisterSensor("test", 0x00, 1.0, signed=False, groups=["string"])

        # when
        result = sut.format_value(3.14)

        # then
        assert result == "3.1"
