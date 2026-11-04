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


from deye_config import DeyeConfig, DeyeLoggerConfig
from deye_daemon import DeyeDaemon


def test_each_logger_reads_with_its_own_modbus_id(mocker):
    # given
    mocker.patch("deye_daemon.DeyeMqttClient")
    processor_factory = mocker.patch("deye_daemon.DeyeProcessorFactory").return_value
    processor_factory.create_processors.return_value = []
    connector_factory = mocker.patch("deye_daemon.DeyeConnectorFactory").return_value
    connector_factory.create_connector.side_effect = lambda logger_config: mocker.Mock(
        **{"send_request.return_value": None}
    )
    config = DeyeConfig(
        logger_configs=[
            DeyeLoggerConfig(1234567890, "192.168.1.50", 502, index=1, protocol="mbtcp", modbus_id=0),
            DeyeLoggerConfig(1234567891, "192.168.1.50", 502, index=2, protocol="mbtcp", modbus_id=2),
            DeyeLoggerConfig(1234567892, "192.168.1.51", 502, index=3, protocol="mbtcp"),
        ],
        mqtt=None,
        metric_groups={"string"},
    )

    # when
    DeyeDaemon(config)

    # then
    sent_modbus_ids = []
    for call in processor_factory.create_processors.call_args_list:
        modbus = call.args[1]
        modbus.read_registers(100, 100)
        sent_modbus_ids.append(modbus.connector.send_request.call_args.args[0][0])
    assert sent_modbus_ids == [0, 2, 1]
