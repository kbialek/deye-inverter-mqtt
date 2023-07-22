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

logger = logging.getLogger(__name__)


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
        return self.online == getattr(other, "online", None)

    def __bool__(self) -> bool:
        return self.online

    def __hash__(self):
        return hash(self.online)


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
    def get_id(self):
        """
        The ID is used to activate the processor in the configuration
        """
        pass

    @abstractmethod
    def process(self, events: list[DeyeEvent]):
        pass


def events_to_str(events: list[DeyeEvent] | set[DeyeEvent]) -> str:
    return ", ".join([str(e) for e in events])


def compare_event_list(events_a: list[DeyeEvent], events_b: list[DeyeEvent], check_status: bool = False) -> bool:
    """
    Compare two lists of DeyeEvents if they are equal, ignoring the order of events

    Parameters
    ----------
    events_a : list[DeyeEvent]
        First list of events
    events_b : list[DeyeEvent]
        Second list of events
    check_status : bool
        If if False, ignore list entries of type DeyeLoggerStatusEvent

    Returns
    -------
    bool
        True if both lists are containing the same events with same values
    """
    set_a = {e for e in events_a if not isinstance(e, DeyeLoggerStatusEvent) or check_status}
    set_b = {e for e in events_b if not isinstance(e, DeyeLoggerStatusEvent) or check_status}
    logger.debug("Compare events A[%s] == B[%s]", events_to_str(set_a), events_to_str(set_b))

    return set_a == set_b
