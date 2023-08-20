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
import json
from datetime import datetime

from deye_plugin_loader import DeyePluginContext
from deye_events import DeyeEvent, DeyeEventProcessor, DeyeEvent, DeyeObservationEvent, DeyeLoggerStatusEvent
from deye_config import DeyeConfig
from deye_observation import Observation
from deye_mqtt import DeyeMqttClient


class ahoyDTUMQTTPublisher(DeyeEventProcessor):
    """
    Publishes events to MQTT in ahoyDTU format
    """

    __names={
        ### CONVERT 2.5 vs 2500 - convert x1000
        "day_energy":          "ch0/YieldDay",
        "total_energy":        "ch0/YieldTotal",
        ### CONVERT 0.0 vs 249870 - ERROR Deye
        # "uptime":            "solar/uptime",

        "ac/l1/voltage":       "ch0/U_AC",
        "ac/l1/current":       "ch0/I_AC",
        "ac/l1/power":         "ch0/P_AC",
        "ac/freq":             "ch0/F_AC",
        "ac/active_power":     "ch0/P_DC",

        "dc/pv1/voltage":      "ch1/U_DC",
        "dc/pv1/current":      "ch1/I_DC",
        "dc/pv1/power":        "ch1/P_DC",
        ### CONVERT 2.5 vs 2500 - convert x1000
        "dc/pv1/day_energy":   "ch1/YieldDay",
        "dc/pv1/total_energy": "ch1/YieldTotal",

        "dc/pv2/voltage":      "ch2/U_DC",
        "dc/pv2/current":      "ch2/I_DC",
        "dc/pv2/power":        "ch2/P_DC",
        ### CONVERT 2.5 vs 2500 - convert x1000
        "dc/pv2/day_energy":   "ch2/YieldDay",
        "dc/pv2/total_energy": "ch2/YieldTotal",

        "dc/pv3/voltage":      "ch3/U_DC",
        "dc/pv3/current":      "ch3/I_DC",
        "dc/pv3/power":        "ch3/P_DC",
        ### CONVERT 2.5 vs 2500 - convert x1000
        "dc/pv3/day_energy":   "ch3/YieldDay",
        "dc/pv3/total_energy": "ch3/YieldTotal",

        "dc/pv4/voltage":      "ch4/U_DC",
        "dc/pv4/current":      "ch4/I_DC",
        "dc/pv4/power":        "ch4/P_DC",
        ### CONVERT 2.5 vs 2500 - convert x1000
        "dc/pv4/day_energy":   "ch4/YieldDay",
        "dc/pv4/total_energy": "ch4/YieldTotal",

        "dc/total_power":      "ch0/P_DC",
        "radiator_temp":       "ch0/Temp"
        ### Deye parameters not provided by ahoyDTU
        # "operating_power 0.0"
        # "settings/active_power_regulation 10.0"
        # "logger_status online"
        ### ahoyDTU parameters not provided by Deye
        # ch0/Q_AC 0
        # ch0/PF_AC 1
        # ch0/ALARM_MES_ID 73
        # ch0/Efficiency 95.509
        # solar/total/P_AC 404.1
        # ch1/Irradiation 50.095
        # ch2/Irradiation 50.643
    }

    def __init__(self, config: DeyeConfig, mqtt_client: DeyeMqttClient):
        """Initializes the plugin

        Args:
            config (DeyeConfig): provides access to general config
            mqtt_client (DeyeMqttClient): provides access to existing mqtt client (if configured)
        """
        self.__log = logging.getLogger(ahoyDTUMQTTPublisher.__name__)
        self.__config = config

        ######################################
        # change target mqtt topic here
        self.__mqttTopicPrefix = f"solar/Deye-Sun600"

        if mqtt_client is not None:
            self.__mqtt_client = mqtt_client
        else:
            self.__log.error("No mqtt client defined - enable it in config file")

    def get_id(self):
        return "ahuyDTU_mqtt_publisher"


    def process(self, events: list[DeyeEvent]):
        now = datetime.now()

        for event in events:
            if isinstance(event, DeyeObservationEvent):
                ahoyDTUmqttTopic = ahoyDTUMQTTPublisher.__names.get(event.observation.sensor.mqtt_topic_suffix)
                if ahoyDTUmqttTopic is not None:
                    inverterValue=float(event.observation.value)
                    # YieldDay needs a conversion. Deye: 2.5, ahoy: 2500
                    if ahoyDTUmqttTopic in ["ch0/YieldDay", "ch1/YieldDay", "ch2/YieldDay", "ch3/YieldDay", "ch4/YieldDay"]:
                        inverterValue=float(inverterValue*1000)

                    # this is still a hack to access existing mqtt client
                    fullMQTTTopic = f"{self.__mqttTopicPrefix}/{ahoyDTUmqttTopic}"
                    self.__mqtt_client._DeyeMqttClient__do_publish(mqtt_topic=fullMQTTTopic,
                                                                   value=inverterValue)
                else:
                    self.__log.warn("Unknown ahoyDTU parameter - name: {} mqtt topic: {} value: {}".format(
                        event.observation.sensor.name,
                        event.observation.sensor.mqtt_topic_suffix,
                        event.observation.value))
            elif isinstance(event, DeyeLoggerStatusEvent):
                self.__log.info("InvStatus: {}".format("online" if event.online else "Offline"))
            else:
                self.__log.warn(f"Unsupported event type {event.__class__}")


class DeyePlugin:
    def __init__(self, plugin_context: DeyePluginContext):
        self.publisher = ahoyDTUMQTTPublisher(config=plugin_context.config,
                                              mqtt_client=plugin_context.mqtt_client)


    def get_event_processors(self) -> [DeyeEventProcessor]:
        return [self.publisher]
