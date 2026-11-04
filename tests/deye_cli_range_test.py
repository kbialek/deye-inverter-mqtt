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

import logging
import pytest
from unittest.mock import MagicMock, call, patch

from deye_cli import DeyeCli
from deye_sensor import DoubleRegisterSensor, SingleRegisterSensor


def registers_of(first_reg: int, last_reg: int) -> dict[int, bytearray]:
    return {r: bytearray(r.to_bytes(2, "big")) for r in range(first_reg, last_reg + 1)}


class TestDeyeCli:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.config = MagicMock()
        self.config.logger.ip_address = "127.0.0.1"
        self.config.logger.max_register_range_length = 4
        self.config.metric_groups = []
        self.cli = DeyeCli(self.config)
        self.modbus = MagicMock()
        self.modbus.read_registers.side_effect = registers_of
        with patch("deye_cli.sensor_list", []):
            yield

    def test_single_register_read_keeps_output(self, caplog):
        # given
        self.modbus.read_registers.side_effect = None
        self.modbus.read_registers.return_value = {108: bytearray([0x01, 0x2C])}

        # when
        with caplog.at_level(logging.INFO):
            self.cli.read_register(self.modbus, ["108"], 4)

        # then
        self.modbus.read_registers.assert_called_once_with(108, 108)
        assert "int: 300, l: 44, h: 1" in caplog.text

    def test_range_read_is_split_into_chunks(self, capsys):
        # when
        self.cli.read_register(self.modbus, ["0", "9"], 4)

        # then
        assert self.modbus.read_registers.call_args_list == [call(0, 3), call(4, 7), call(8, 9)]
        lines = capsys.readouterr().out.splitlines()
        assert len(lines) == 10
        assert lines[0] == "0\t0 (0x0000)"
        assert lines[9] == "9\t9 (0x0009)"

    def test_range_read_continues_after_failed_chunk(self, capsys, caplog):
        # given
        self.modbus.read_registers.side_effect = lambda first, last: {} if first == 4 else registers_of(first, last)

        # when
        with caplog.at_level(logging.INFO):
            self.cli.read_register(self.modbus, ["0", "9"], 4)

        # then
        lines = capsys.readouterr().out.splitlines()
        assert [int(line.split("\t")[0]) for line in lines] == [0, 1, 2, 3, 8, 9]
        assert "Registers 4-7 not read" in caplog.text
        assert "Read 6 of 10 registers, 1 chunk(s) not read" in caplog.text

    def test_range_read_exits_when_nothing_read(self):
        # given
        self.modbus.read_registers.side_effect = lambda first, last: {}

        # when
        with pytest.raises(SystemExit) as exit_info:
            self.cli.read_register(self.modbus, ["0", "9"], 4)

        # then
        assert exit_info.value.code == 1

    def test_range_read_uses_at_least_one_register_per_chunk(self):
        # when
        self.cli.read_register(self.modbus, ["5", "6"], 0)

        # then
        assert self.modbus.read_registers.call_args_list == [call(5, 5), call(6, 6)]

    def test_range_read_chunks_are_capped_at_modbus_maximum(self):
        # when
        self.cli.read_register(self.modbus, ["0", "299"], 256)

        # then
        assert self.modbus.read_registers.call_args_list == [call(0, 124), call(125, 249), call(250, 299)]

    def test_range_read_describes_registers_with_active_metric_groups(self, capsys):
        # given
        self.config.metric_groups = ["test"]
        voltage = SingleRegisterSensor(
            "Shutdown voltage", 2, 0.01, mqtt_topic_suffix="a", unit="V", print_format="{:0.2f}", groups=["test"]
        )
        other_group = SingleRegisterSensor("Other group", 3, 1, mqtt_topic_suffix="b", unit="W", groups=["other"])
        self.modbus.read_registers.side_effect = lambda first, last: {
            r: bytearray((4650 if r == 2 else r).to_bytes(2, "big")) for r in range(first, last + 1)
        }

        # when
        with patch("deye_cli.sensor_list", [voltage, other_group]):
            self.cli.read_register(self.modbus, ["0", "3"], 4)

        # then
        lines = capsys.readouterr().out.splitlines()
        assert lines[2] == "2\t4650 (0x122a)\tShutdown voltage: 46.50 V"
        assert lines[3] == "3\t3 (0x0003)"

    def test_range_read_decodes_double_register_sensor_across_chunks(self, capsys):
        # given
        self.config.metric_groups = ["test"]
        energy = DoubleRegisterSensor(
            "Total energy", 3, 0.1, mqtt_topic_suffix="c", unit="kWh", print_format="{:0.1f}", groups=["test"]
        )
        words = {3: 0x0001, 4: 0x0002}  # low word first: 0x0002_0001 = 131073 -> 13107.3 kWh
        self.modbus.read_registers.side_effect = lambda first, last: {
            r: bytearray(words.get(r, 0).to_bytes(2, "big")) for r in range(first, last + 1)
        }

        # when
        with patch("deye_cli.sensor_list", [energy]):
            self.cli.read_register(self.modbus, ["0", "7"], 4)

        # then
        assert self.modbus.read_registers.call_args_list == [call(0, 3), call(4, 7)]
        lines = capsys.readouterr().out.splitlines()
        assert lines[3] == "3\t1 (0x0001)\tTotal energy: 13107.3 kWh"
        assert lines[4] == "4\t2 (0x0002)"

    def test_range_read_skips_sensor_that_cannot_be_decoded(self, capsys):
        # given
        self.config.metric_groups = ["test"]
        broken = MagicMock()
        broken.get_registers.return_value = [1]
        broken.in_any_group.return_value = True
        broken.read_value.side_effect = ValueError("bad value")

        # when
        with patch("deye_cli.sensor_list", [broken]):
            self.cli.read_register(self.modbus, ["0", "3"], 4)

        # then
        lines = capsys.readouterr().out.splitlines()
        assert lines == ["0\t0 (0x0000)", "1\t1 (0x0001)", "2\t2 (0x0002)", "3\t3 (0x0003)"]

    @pytest.mark.parametrize("args", [["9", "0"], ["-1"], ["65536"], ["0", "65536"], ["abc"], []])
    def test_invalid_addresses_are_rejected(self, args):
        # when
        with pytest.raises(SystemExit) as exit_info:
            self.cli.read_register(self.modbus, args, 4)

        # then
        assert exit_info.value.code == 1
        self.modbus.read_registers.assert_not_called()

    @patch("deye_cli.DeyeModbus")
    @patch("deye_cli.DeyeConnectorFactory")
    def test_exec_command_chunks_by_logger_max_register_range_length(self, connector_factory_mock, modbus_class_mock):
        # given
        self.config.logger.max_register_range_length = 2
        modbus_class_mock.return_value = self.modbus

        # when
        self.cli.exec_command(["r", "10", "13"])

        # then
        assert self.modbus.read_registers.call_args_list == [call(10, 11), call(12, 13)]
