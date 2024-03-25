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

from deye_plugin_loader import DeyePluginContext
from deye_events import DeyeEventProcessor, DeyeEventList, DeyeObservationEvent


class DeyeSamplePublisher(DeyeEventProcessor):
    """An example of custom DeyeEventProcessor implementation
    """
    def get_id(self):
        return "sample_publisher"

    def process(self, events: DeyeEventList):
        print(f"Processing events from logger: {events.logger_index}")
        for event in events:
            if isinstance(event, DeyeObservationEvent):
                observation_event: DeyeObservationEvent = event
                print(
                    {
                        "name": observation_event.observation.sensor.mqtt_topic_suffix,
                        "value": observation_event.observation.value,
                    }
                )


class DeyePlugin:
    """Plugin entrypoint

    The plugin loader first instantiates DeyePlugin class, and then gets event processors from it. 
    """
    def __init__(self, plugin_context: DeyePluginContext):
        """Initializes the plugin

        Args:
            plugin_context (DeyePluginContext): provides access to core service components, e.g. config
        """
        self.publisher = DeyeSamplePublisher()

    def get_event_processors(self) -> [DeyeEventProcessor]:
        """Provides a list of custom event processors 
        """
        return [self.publisher]
