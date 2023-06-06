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
import logging
import json
from unittest.mock import patch
from io import StringIO
from datetime import datetime

from deye_stdout_publisher import DeyeStdoutPublisher
from deye_config import DeyeConfig, DeyeLoggerConfig
from deye_events import DeyeEvent, DeyeObservationEvent, DeyeLoggerStatusEvent
from deye_observation import Observation
from deye_sensor import ComputedSumSensor, Sensor


class UnsupportedEvent(DeyeEvent):
    pass


class DeyeStdoutPublisherTest(unittest.TestCase):
    def setUp(self):
        self.config = DeyeConfig(logger_config=DeyeLoggerConfig(1234567890, "192.168.1.1", 8899), mqtt=None)

    def test_get_id(self):
        sut = DeyeStdoutPublisher(self.config)
        self.assertEqual(sut.get_id(), "stdout_publisher")

    def __test_process(self, events: list[DeyeEvent]):
        buffer = StringIO()

        sut = DeyeStdoutPublisher(self.config, dest=buffer)
        sut.process(events)

        return json.loads(buffer.getvalue())

    def test_header(self):
        out = self.__test_process([])

        self.assertEqual(out.pop("serial"), "1234567890")
        self.assertEqual(out.pop("address"), "192.168.1.1")
        self.assertEqual(out.pop("port"), 8899)
        self.assertEqual(out.pop("data"), [])
        self.assertEqual(len(out), 0)

    def test_unsupported_event(self):
        logger = logging.getLogger(DeyeStdoutPublisher.__name__)

        with patch.object(logger, "warn") as mock_warn:
            out = self.__test_process([UnsupportedEvent()])
            self.assertEqual(out.pop("data"), [])

        self.assertEqual(mock_warn.call_count, 1)
        self.assertIn("Unsupported event type", mock_warn.call_args.args[0])

    def test_status_events(self):
        out = self.__test_process(
            [
                DeyeLoggerStatusEvent(online=True),
                DeyeLoggerStatusEvent(online=False),
            ]
        )

        data = out.pop("data")

        self.assertEqual(len(data), 2)
        self.assertEqual(data[0], {"up": 1})
        self.assertEqual(data[1], {"up": 0})

    def test_observation_events(self):
        out = self.__test_process(
            [
                DeyeObservationEvent(
                    observation=Observation(
                        sensor=Sensor(
                            name="some sensor",
                            mqtt_topic_suffix="some/topic_and_things_thisIsTheValue",
                            unit="some unit",
                            groups=["group1", "group2"],
                        ),
                        timestamp=datetime.fromtimestamp(42),
                        value=123,
                    )
                ),
                DeyeObservationEvent(
                    observation=Observation(
                        sensor=ComputedSumSensor(
                            name="some sum sensor",
                            sensors=[
                                Sensor(
                                    name="ignored",
                                    mqtt_topic_suffix="the/inner/topic/ignored",
                                    unit="ignored",
                                    groups=["some other group"],
                                )
                            ],
                            mqtt_topic_suffix="the/other/topic_thing",
                            unit="some other unit",
                            groups=["some group"],
                        ),
                        timestamp=datetime.fromtimestamp(43),
                        value="some value",
                    )
                ),
                DeyeObservationEvent(
                    observation=Observation(
                        sensor=Sensor(
                            name="blipp",
                            mqtt_topic_suffix="single",
                            unit="blupp",
                            groups=["blapp"],
                        ),
                        timestamp=datetime.fromtimestamp(44),
                        value=None,
                    )
                ),
            ]
        )

        data = out.pop("data")

        self.assertEqual(len(data), 3)

        o1 = data[0]
        self.assertEqual(o1.pop("thisIsTheValue"), 123)
        self.assertEqual(o1.pop("name"), "some sensor")
        self.assertEqual(o1.pop("source"), "some/topic/and/things")
        self.assertEqual(o1.pop("unit"), "some unit")
        self.assertEqual(o1.pop("groups"), "group1,group2")
        self.assertEqual(o1.pop("sensor"), "Sensor")
        self.assertEqual(o1.pop("timestamp"), 42)
        self.assertEqual(len(o1), 0)

        o2 = data[1]
        self.assertEqual(o2.pop("thing"), "some value")
        self.assertEqual(o2.pop("name"), "some sum sensor")
        self.assertEqual(o2.pop("source"), "the/other/topic")
        self.assertEqual(o2.pop("unit"), "some other unit")
        self.assertEqual(o2.pop("groups"), "some group")
        self.assertEqual(o2.pop("sensor"), "ComputedSumSensor")
        self.assertEqual(o2.pop("timestamp"), 43)
        self.assertEqual(len(o2), 0)

        o3 = data[2]
        self.assertEqual(o3.pop("single"), None)
        self.assertEqual(o3.pop("name"), "blipp")
        self.assertEqual(o3.pop("unit"), "blupp")
        self.assertEqual(o3.pop("groups"), "blapp")
        self.assertEqual(o3.pop("sensor"), "Sensor")
        self.assertEqual(o3.pop("timestamp"), 44)
        self.assertEqual(len(o3), 0)


if __name__ == "__main__":
    unittest.main()
