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
from unittest.mock import patch
from deye_sensor import Sensor, ComputedSumSensor

class TestSensor(Sensor):

    def __init__(self, name, value):
        super().__init__(name)
        self.value = value

    def read_value(self, registers):
        return self.value


class DeyeSensorTest(unittest.TestCase):

    def test_sum_sensor_returns_sum_when_all_inputs_are_given(self):
        # given
        test_sensor1 = TestSensor("ts1", 1.1)
        test_sensor2 = TestSensor("ts2", 2.2)

        # and
        sut = ComputedSumSensor('sum', [test_sensor1, test_sensor2])

        # when
        result = sut.read_value([])

        # then
        self.assertAlmostEqual(result, 3.3)

    def test_sum_sensor_returns_none_when_any_input_is_none(self):
        # given
        test_sensor1 = TestSensor("ts1", 1.1)
        test_sensor2 = TestSensor("ts2", None)

        # and
        sut = ComputedSumSensor('sum', [test_sensor1, test_sensor2])

        # when
        result = sut.read_value([])

        # then
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()