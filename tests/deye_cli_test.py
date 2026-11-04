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


from unittest.mock import patch

import pytest

from deye_cli import DeyeCli
from deye_config import DeyeConfig, DeyeLoggerConfig


@pytest.fixture
def config() -> DeyeConfig:
    # Two inverters behind one Modbus gateway, configured as two loggers
    return DeyeConfig(
        logger_configs=[
            DeyeLoggerConfig(1234567890, "192.168.1.50", 502, index=1, protocol="mbtcp", modbus_id=0),
            DeyeLoggerConfig(1234567891, "192.168.1.50", 502, index=2, protocol="mbtcp", modbus_id=247),
        ],
        mqtt=None,
    )


@pytest.mark.parametrize(
    "args,expected_frame",
    [
        (["w", "100", "5"], "001000640001020005"),
        (["1", "w", "100", "5"], "001000640001020005"),
        (["2", "w", "100", "5"], "f71000640001020005"),
    ],
)
def test_write_register_uses_modbus_id_of_selected_logger(config, args, expected_frame):
    with patch("deye_cli.DeyeConnectorFactory") as factory:
        connector = factory.return_value.create_connector.return_value
        connector.send_request.return_value = None

        DeyeCli(config).exec_command(args)

    assert connector.send_request.call_args.args[0][:-2] == bytearray.fromhex(expected_frame)


def test_read_register_uses_modbus_id_of_selected_logger(config):
    with patch("deye_cli.DeyeConnectorFactory") as factory:
        connector = factory.return_value.create_connector.return_value
        connector.send_request.return_value = None

        with pytest.raises(SystemExit):
            DeyeCli(config).exec_command(["2", "r", "100"])

    factory.return_value.create_connector.assert_called_once_with(config.logger_configs[1])
    assert connector.send_request.call_args.args[0][:-2] == bytearray.fromhex("f70300640001")
