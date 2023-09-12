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

from deye_config import DeyeEnv


class DeyeConfigTest(unittest.TestCase):
    def test_read_existing_required_string(self):
        value = DeyeEnv.string("PWD")
        assert value is not None

    def test_read_not_existing_required_string(self):
        try:
            DeyeEnv.string("FOO")
            self.fail()
        except KeyError as e:
            pass

    def test_read_existing_optional_string(self):
        value = DeyeEnv.string("PWD", "bar")
        assert value is not None
        assert value != "bar"

    def test_read_not_existing_optional_string(self):
        value = DeyeEnv.string("FOO", "bar")
        assert value == "bar"

    def test_read_non_existing_integer_with_default(self):
        value = DeyeEnv.integer("FOO", 123)
        assert value == 123

    def test_read_not_existing_integer_without_default(self):
        try:
            DeyeEnv.integer("FOO")
            self.fail()
        except KeyError as e:
            pass

    def test_read_non_existing_boolean_with_default_true(self):
        value = DeyeEnv.boolean("FOO", True)
        assert value

    def test_read_non_existing_boolean_with_default_false(self):
        value = DeyeEnv.boolean("FOO", False)
        assert not value

    def test_read_not_existing_boolean_without_default(self):
        try:
            DeyeEnv.boolean("FOO")
            self.fail()
        except KeyError as e:
            pass
