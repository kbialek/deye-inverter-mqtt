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

from deye_plugin_loader import DeyePluginContext, DeyeEventProcessorContext
from deye_events import DeyeEventProcessor, DeyeEventList, DeyeObservationEvent


class DeyeEventProcessorContextAwarePublisher(DeyeEventProcessor):
    """An example of custom DeyeEventProcessor implementation
    """
    def __init__(self):
        self.__log = logging.getLogger(DeyeEventProcessorContextAwarePublisher.__name__)

    def get_id(self):
        return "event_processor_context_aware_sample_publisher"

    def set_event_processor_context(self, context: DeyeEventProcessorContext):
        self.__event_processor_context = context
        self.__log.info(f"Modbus available in the plugin: {context.modbus}")
        self.__log.info(f"Logger config available in the plugin: {context.logger_config}")
        
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
        self.publisher = DeyeEventProcessorContextAwarePublisher()

    def get_event_processors_v2(self, event_processor_context: DeyeEventProcessorContext) -> [DeyeEventProcessor]:
        """Provides a list of custom event processors 
        """
        self.publisher.set_event_processor_context(event_processor_context)
        return [self.publisher]
