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
from deye_sensor import DateTimeSensor, DoubleRegisterSensor, SingleRegisterSensor


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

    @pytest.mark.parametrize("args", [["9", "0"], ["-1"], ["65536"], ["0", "65536"], ["abc"], [], ["0", "9", "1"]])
    def test_invalid_addresses_are_rejected(self, args):
        # when
        with pytest.raises(SystemExit) as exit_info:
            self.cli.read_register(self.modbus, args, 4)

        # then
        assert exit_info.value.code == 1
        self.modbus.read_registers.assert_not_called()

    def test_range_read_of_one_register(self, capsys):
        # when
        self.cli.read_register(self.modbus, ["5", "5"], 4)

        # then
        self.modbus.read_registers.assert_called_once_with(5, 5)
        assert capsys.readouterr().out.splitlines() == ["5\t5 (0x0005)"]

    def test_read_without_range_length_uses_modbus_maximum(self):
        # when
        self.cli.read_register(self.modbus, ["0", "299"])

        # then
        assert self.modbus.read_registers.call_args_list == [call(0, 124), call(125, 249), call(250, 299)]

    def test_range_read_does_not_describe_sensor_whose_registers_were_not_all_read(self, capsys):
        # given
        self.config.metric_groups = ["test"]
        straddling = MagicMock()
        straddling.get_registers.return_value = [3, 4]
        straddling.in_any_group.return_value = True
        straddling.read_value.return_value = 42
        self.modbus.read_registers.side_effect = lambda first, last: {} if first == 4 else registers_of(first, last)

        # when
        with patch("deye_cli.sensor_list", [straddling]):
            self.cli.read_register(self.modbus, ["0", "7"], 4)

        # then
        straddling.read_value.assert_not_called()
        lines = capsys.readouterr().out.splitlines()
        assert lines == ["0\t0 (0x0000)", "1\t1 (0x0001)", "2\t2 (0x0002)", "3\t3 (0x0003)"]

    def test_range_read_does_not_describe_sensor_without_value(self, capsys):
        # given
        self.config.metric_groups = ["test"]
        no_value = MagicMock()
        no_value.get_registers.return_value = [1]
        no_value.in_any_group.return_value = True
        no_value.read_value.return_value = None
        no_value.format_value.side_effect = str
        no_value.unit = ""

        # when
        with patch("deye_cli.sensor_list", [no_value]):
            self.cli.read_register(self.modbus, ["0", "3"], 4)

        # then
        lines = capsys.readouterr().out.splitlines()
        assert lines == ["0\t0 (0x0000)", "1\t1 (0x0001)", "2\t2 (0x0002)", "3\t3 (0x0003)"]

    def test_range_read_describes_sensor_without_unit_without_trailing_space(self, capsys):
        # given
        self.config.metric_groups = ["test"]
        work_mode = SingleRegisterSensor(
            "Work Mode", 2, 1, mqtt_topic_suffix="d", print_format="{:.0f}", groups=["test"]
        )

        # when
        with patch("deye_cli.sensor_list", [work_mode]):
            self.cli.read_register(self.modbus, ["0", "3"], 4)

        # then
        assert capsys.readouterr().out.splitlines()[2] == "2\t2 (0x0002)\tWork Mode: 2"

    def test_range_read_shows_date_and_time_sensor_as_iso_date_and_time(self, capsys):
        # given
        self.config.metric_groups = ["test"]
        system_time = DateTimeSensor("System time", 62, groups=["test"])
        words = {62: (26 << 8) + 11, 63: (4 << 8) + 13, 64: (0 << 8) + 56}  # 2026-11-04 13:00:56
        self.modbus.read_registers.side_effect = lambda first, last: {
            r: bytearray(words.get(r, 0).to_bytes(2, "big")) for r in range(first, last + 1)
        }

        # when
        with patch("deye_cli.sensor_list", [system_time]):
            self.cli.read_register(self.modbus, ["60", "65"], 125)

        # then
        lines = capsys.readouterr().out.splitlines()
        assert lines[2] == "62\t6667 (0x1a0b)\tSystem time: 2026-11-04 13:00:56"

    def test_range_read_logs_progress_every_ten_chunks(self, caplog):
        # when
        with caplog.at_level(logging.INFO):
            self.cli.read_register(self.modbus, ["0", "83"], 4)

        # then
        progress = [r.getMessage() for r in caplog.records if "so far" in r.getMessage()]
        assert progress == [
            "Read 40 of 84 registers so far (up to register 39)",
            "Read 80 of 84 registers so far (up to register 79)",
        ]

    def test_range_read_logs_no_progress_after_last_chunk(self, caplog):
        # when
        with caplog.at_level(logging.INFO):
            self.cli.read_register(self.modbus, ["0", "79"], 4)

        # then
        progress = [r.getMessage() for r in caplog.records if "so far" in r.getMessage()]
        assert progress == ["Read 40 of 80 registers so far (up to register 39)"]

    def test_range_read_prints_registers_read_before_interrupt(self, capsys, caplog):
        # given
        def read_until_interrupt(first, last):
            if first == 8:
                raise KeyboardInterrupt
            return registers_of(first, last)

        self.modbus.read_registers.side_effect = read_until_interrupt

        # when
        with caplog.at_level(logging.INFO), pytest.raises(SystemExit) as exit_info:
            try:
                self.cli.read_register(self.modbus, ["0", "19"], 4)
            except KeyboardInterrupt:
                pytest.fail("Ctrl-C was not handled by the range read")

        # then
        assert exit_info.value.code == 130
        lines = capsys.readouterr().out.splitlines()
        assert [int(line.split("\t")[0]) for line in lines] == list(range(8))
        assert "Interrupted while reading registers 8-11" in caplog.text
        assert "Read 8 of 20 registers, 0 chunk(s) not read" in caplog.text

    def test_write_register(self, caplog):
        # given
        self.modbus.write_register_uint.return_value = True

        # when
        with caplog.at_level(logging.INFO):
            self.cli.write_register(self.modbus, ["108", "300"])

        # then
        self.modbus.write_register_uint.assert_called_once_with(108, 300)
        assert "Ok" in caplog.text

    @pytest.mark.parametrize(
        "args",
        [["abc", "1"], ["1", "abc"], ["-1", "1"], ["65536", "1"], ["1", "-1"], ["1", "65536"], ["1"], ["1", "2", "3"]],
    )
    def test_invalid_write_arguments_are_rejected(self, args):
        # when
        with pytest.raises(SystemExit) as exit_info:
            self.cli.write_register(self.modbus, args)

        # then
        assert exit_info.value.code == 1
        self.modbus.write_register_uint.assert_not_called()

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

    @patch("deye_cli.DeyeModbus")
    @patch("deye_cli.DeyeConnectorFactory")
    def test_exec_command_chunks_by_range_length_of_selected_logger(self, connector_factory_mock, modbus_class_mock):
        # given
        second_logger = MagicMock()
        second_logger.max_register_range_length = 3
        self.config.logger_configs = [self.config.logger, second_logger]
        modbus_class_mock.return_value = self.modbus

        # when
        self.cli.exec_command(["2", "r", "0", "5"])

        # then
        connector_factory_mock.return_value.create_connector.assert_called_once_with(second_logger)
        assert self.modbus.read_registers.call_args_list == [call(0, 2), call(3, 5)]

    @patch("deye_cli.DeyeModbus")
    @patch("deye_cli.DeyeConnectorFactory")
    def test_exec_command_writes_register(self, connector_factory_mock, modbus_class_mock):
        # given
        modbus_class_mock.return_value = self.modbus

        # when
        self.cli.exec_command(["w", "108", "300"])

        # then
        self.modbus.write_register_uint.assert_called_once_with(108, 300)

    def test_single_register_read_exits_when_register_not_read(self, caplog):
        # given
        self.modbus.read_registers.side_effect = lambda first, last: {}

        # when
        with pytest.raises(SystemExit) as exit_info:
            self.cli.read_register(self.modbus, ["108"])

        # then
        assert exit_info.value.code == 1
        assert "register 108 not read" in caplog.text

    def test_write_register_reports_failure(self, caplog):
        # given
        self.modbus.write_register_uint.return_value = False

        # when
        self.cli.write_register(self.modbus, ["108", "300"])

        # then
        assert caplog.records[-1].levelname == "ERROR"
        assert caplog.records[-1].getMessage() == "Error"
