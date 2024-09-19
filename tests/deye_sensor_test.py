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

import unittest
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
)


class FakeSensor(AbstractSensor):
    def __init__(self, name, value):
        super().__init__(name, groups=["string"])
        self.value = value

    def read_value(self, registers):
        return self.value


class DeyeSensorTest(unittest.TestCase):
    def test_sum_sensor_returns_sum_when_all_inputs_are_given(self):
        # given
        test_sensor1 = FakeSensor("ts1", 1.1)
        test_sensor2 = FakeSensor("ts2", 2.2)

        # and
        sut = ComputedSumSensor("sum", [test_sensor1, test_sensor2], groups=["string"])

        # when
        result = sut.read_value([])

        # then
        self.assertAlmostEqual(result, 3.3)

    def test_sum_sensor_returns_none_when_any_input_is_none(self):
        # given
        test_sensor1 = FakeSensor("ts1", 1.1)
        test_sensor2 = FakeSensor("ts2", None)

        # and
        sut = ComputedSumSensor("sum", [test_sensor1, test_sensor2], groups=["string"])

        # when
        result = sut.read_value([])

        # then
        self.assertIsNone(result)

    def test_single_reg_sensor_unsigned(self):
        # given
        sut = SingleRegisterSensor("test", 0x00, 1, signed=False, groups=["string"])

        # and
        registers = {0: bytearray.fromhex("0102")}

        # when
        result = sut.read_value(registers)

        # then
        self.assertEqual(result, 0x0102)

    def test_single_reg_sensor_signed(self):
        # given
        sut = SingleRegisterSensor("test", 0x00, 1, signed=True, groups=["string"])

        # and
        registers = {0: bytearray.fromhex("fffe")}

        # when
        result = sut.read_value(registers)

        # then
        self.assertEqual(result, -2)

    def test_double_reg_sensor_unsigned(self):
        # given
        sut = DoubleRegisterSensor("test", 0x00, 1, signed=False, groups=["string"])

        # and
        registers = {0: bytearray.fromhex("0102"), 1: bytearray.fromhex("0304")}  # low word  # high word

        # when
        result = sut.read_value(registers)

        # then
        self.assertEqual(result, 0x03040102)

    def test_double_reg_sensor_signed(self):
        # given
        sut = DoubleRegisterSensor("test", 0x00, 1, signed=True, groups=["string"])

        # and
        registers = {0: bytearray.fromhex("fffe"), 1: bytearray.fromhex("ffff")}  # low word  # high word

        # when
        result = sut.read_value(registers)

        # then
        self.assertEqual(result, -2)

    def test_double_reg_sensor_unsigned_high_word_first(self):
        # given
        sut = DoubleRegisterSensor("test", 0x00, 1, signed=False, groups=["string"], low_word_first=False)

        # and
        registers = {0: bytearray.fromhex("0102"), 1: bytearray.fromhex("0304")}  # low word  # high word

        # when
        result = sut.read_value(registers)

        # then
        self.assertEqual(result, 0x01020304)

    def test_signed_magnitude_single_register_signed(self):
        # given
        sut = SignedMagnitudeSingleRegisterSensor("test", 0x00, 1, groups=["igen_dtsd422"])

        # and
        registers = {0: bytearray.fromhex("8310")}

        # when
        result = sut.read_value(registers)

        # then
        self.assertEqual(result, -784)

    def test_signed_magnitude_single_register_unsigned(self):
        # given
        sut = SignedMagnitudeSingleRegisterSensor("test", 0x00, 1, groups=["igen_dtsd422"])

        # and
        registers = {0: bytearray.fromhex("0310")}

        # when
        result = sut.read_value(registers)

        # then
        self.assertEqual(result, 784)

    def test_signed_magnitude_double_register_signed(self):
        # given
        sut = SignedMagnitudeDoubleRegisterSensor("test", 0x00, 1, groups=["igen_dtsd422"])

        # and
        registers = {0: bytearray.fromhex("8000"), 1: bytearray.fromhex("0101")}  # high word  # low word

        # when
        result = sut.read_value(registers)

        # then
        self.assertEqual(result, -257)

    def test_signed_magnitude_double_register_unsigned(self):
        # given
        sut = SignedMagnitudeDoubleRegisterSensor("test", 0x00, 1, groups=["igen_dtsd422"])

        # and
        registers = {0: bytearray.fromhex("0000"), 1: bytearray.fromhex("0101")}  # high word  # low word

        # when
        result = sut.read_value(registers)

        # then
        self.assertEqual(result, 257)

    def test_single_reg_sensor_write_unsigned(self):
        # given
        sut = SingleRegisterSensor("test", 0x00, 1, signed=False, groups=["string"])

        # when
        result = sut.write_value("1234")

        # then
        self.assertEqual(result, {0: bytearray.fromhex("04d2")})

    def test_single_reg_sensor_write_signed(self):
        # given
        sut = SingleRegisterSensor("test", 0x00, 1, signed=True, groups=["string"])

        # when
        result = sut.write_value("-1234")

        # then
        self.assertEqual(result, {0: bytearray.fromhex("fb2e")})

    def test_split_long_register_range(self):
        # given
        sut = SensorRegisterRange("test", 10, 50)

        # when
        result = sut.split(21)

        # then
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].length, 21)
        self.assertEqual(result[0].first_reg_address, 10)
        self.assertEqual(result[0].last_reg_address, 30)
        self.assertEqual(result[1].length, 20)
        self.assertEqual(result[1].first_reg_address, 31)
        self.assertEqual(result[1].last_reg_address, 50)

    def test_split_short_register_range(self):
        # given
        sut = SensorRegisterRange("test", 10, 50)

        # when
        result = sut.split(45)

        # then
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].length, 41)
        self.assertEqual(result[0].first_reg_address, 10)
        self.assertEqual(result[0].last_reg_address, 50)

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
        self.assertEqual(len(sut.ranges), 4)
        self.assertEqual(sut.ranges[0].group, {"a"})
        self.assertEqual(sut.ranges[0].first_reg_address, 1)
        self.assertEqual(sut.ranges[0].last_reg_address, 10)
        self.assertEqual(sut.ranges[1].group, {"b"})
        self.assertEqual(sut.ranges[1].first_reg_address, 20)
        self.assertEqual(sut.ranges[1].last_reg_address, 34)
        self.assertEqual(sut.ranges[2].group, {"b"})
        self.assertEqual(sut.ranges[2].first_reg_address, 35)
        self.assertEqual(sut.ranges[2].last_reg_address, 40)
        self.assertEqual(sut.ranges[3].group, {"c"})
        self.assertEqual(sut.ranges[3].first_reg_address, 60)
        self.assertEqual(sut.ranges[3].last_reg_address, 70)

    def test_registry_range_single_group_name(self):
        # given
        sut = SensorRegisterRange("a", 1, 2)

        # expect
        self.assertTrue(sut.in_any_group({"a"}))
        self.assertFalse(sut.in_any_group({"b"}))

    def test_registry_range_multiple_groups_names(self):
        # given
        sut = SensorRegisterRange({"a", "b"}, 1, 2)

        # expect
        self.assertTrue(sut.in_any_group({"a"}))
        self.assertTrue(sut.in_any_group({"b"}))
        self.assertFalse(sut.in_any_group({"c"}))

    def test_reset_sensor_passthrough(self):
        # given
        sut = SingleRegisterSensor("test", 0x00, 1, signed=False, groups=["string"]).reset_daily()

        # and
        registers = {0: bytearray.fromhex("0102")}

        # when
        result = sut.read_value(registers)

        # then
        self.assertEqual(result, 0x0102)


if __name__ == "__main__":
    unittest.main()
