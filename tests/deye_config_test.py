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

import os
import pytest

from deye_config import DeyeConfig, DeyeEnv, DeyeMqttConfig, DeyeLoggerConfig


class TestDeyeConfig:
    def test_read_existing_required_string(self):
        value = DeyeEnv.string("PWD")
        assert value is not None

    def test_read_not_existing_required_string(self):
        with pytest.raises(KeyError):
            DeyeEnv.string("FOO")

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
        with pytest.raises(KeyError):
            DeyeEnv.integer("FOO")

    def test_read_non_existing_boolean_with_default_true(self):
        value = DeyeEnv.boolean("FOO", True)
        assert value

    def test_read_non_existing_boolean_with_default_false(self):
        value = DeyeEnv.boolean("FOO", False)
        assert not value

    def test_read_not_existing_boolean_without_default(self):
        with pytest.raises(KeyError):
            DeyeEnv.boolean("FOO")

    def test_boolean_raises_typeerror_for_non_bool_value(self):
        """Test TypeError when boolean env var is neither 'true' nor 'false' (lines 42-45)."""
        os.environ["TEST_BOOL_VAR"] = "yes"
        try:
            with pytest.raises(TypeError) as e_info:
                DeyeEnv.boolean("TEST_BOOL_VAR")
            assert "not a valid boolean" in str(e_info.value)
        finally:
            del os.environ["TEST_BOOL_VAR"]

    def test_mqtt_config_username_password_return_none_for_empty_strings(self):
        """Test DeyeMqttConfig property getters returning None for empty strings (lines 97, 101)."""
        cfg = DeyeMqttConfig(host="localhost", port=1883, username="", password="", topic_prefix="deye")
        assert cfg.username is None
        assert cfg.password is None

    def test_active_processors_includes_mqtt_publisher_by_default(self):
        """Test feature flag paths: mqtt_publisher is included by default (lines 181-213)."""
        processors = DeyeConfig._DeyeConfig__read_active_processors()
        assert "mqtt_publisher" in processors

    def test_logger_config_serial_number_negative_raises(self):
        with pytest.raises(ValueError):
            DeyeLoggerConfig(-1, "192.168.1.1", 8899)

    def test_logger_config_serial_number_too_large_raises(self):
        with pytest.raises(ValueError):
            DeyeLoggerConfig(0x10000000000, "192.168.1.1", 8899)
