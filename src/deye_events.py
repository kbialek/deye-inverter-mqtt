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
from abc import abstractmethod

from deye_observation import Observation


class DeyeEvent:
    """
    DeyeEvent represents a piece of information collected when reading inverter registers.
    The events are processed by DeyeEventProcessor implementations
    """

    pass


class DeyeObservationEvent(DeyeEvent):
    """
    An event that represents an observation (sensor reading).
    """

    def __init__(self, observation: Observation):
        self.observation = observation

    def __str__(self) -> str:
        return f"{self.observation.sensor.name}: {self.observation.value_as_str()}"

    def __eq__(self, other) -> bool:
        try:
            return (
                self.observation.sensor == other.observation.sensor
                and self.observation.value == other.observation.value
            )
        except AttributeError:
            return False

    def __hash__(self):
        return hash((self.observation.sensor.name, self.observation.value))


class DeyeLoggerStatusEvent(DeyeEvent):
    """
    An event that represents the logger status.
    """

    def __init__(self, online: bool):
        self.online = online

    def __str__(self) -> str:
        return "online" if self.online else "offline"

    def __eq__(self, other) -> bool:
        return self.online == other.online

    def __bool__(self) -> bool:
        return self.online

    def __hash__(self):
        return hash(self.online)


class DeyeEventList(list):
    """
    An list of Deye Events
    """

    def __init__(self, events: list[DeyeEvent] | None = None, logger_index: int = 0):
        self.__log = logging.getLogger(DeyeEventList.__name__)
        self.__logger_index = logger_index
        super().__init__(events if events else [])

    def __str__(self) -> str:
        return ", ".join([str(e) for e in self])

    def get_status(self) -> bool | None:
        """Get value of first status event from event list"""
        for event in self:
            if isinstance(event, DeyeLoggerStatusEvent):
                return event.online
        return None

    @property
    def logger_index(self) -> int:
        return self.__logger_index

    def is_offline(self) -> bool:
        """Check for the status event offline

        Returns
        -------
        bool
            True if status event found and is 'offline' (False).
        """
        return self.get_status() is False

    def compare_observation_events(self, events: "DeyeEventList") -> bool:
        """
        Compare observation events of self with other DeyeEventList, ignoring the order of events

        Parameters
        ----------
        events : list[DeyeEvent]
            Other list of events

        Returns
        -------
        bool
            True if both lists are containing the same events with same values
        """
        if self.logger_index != events.logger_index:
            return False
        set_a = {e for e in self if isinstance(e, DeyeObservationEvent)}
        set_b = {e for e in events if isinstance(e, DeyeObservationEvent)}
        self.__log.debug("Compare events A[%s] == B[%s]", str(self), str(DeyeEventList(events)))
        self.__log.debug("Changed events: %s", str(DeyeEventList(list(set_a - set_b))))
        return set_a == set_b


class DeyeEventProcessor:
    """
    Processors "do something" with the events collected from the inverter.
    """

    def initialize(self):
        """
        Initializes processor dependencies
        """
        pass

    @abstractmethod
    def get_id(self) -> str:
        """
        The ID is used to activate the processor in the configuration
        """
        pass

    def get_description(self) -> str:
        """
        The description of the processor to be printed out in the logs
        """
        return ""

    @abstractmethod
    def process(self, events: DeyeEventList):
        """
        Processes events representing changes of metric values
        """
        pass
