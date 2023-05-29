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


class DeyeLoggerStatusEvent(DeyeEvent):
    """
    An event that represents the logger status.
    """

    def __init__(self, online: bool):
        self.online = online


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
