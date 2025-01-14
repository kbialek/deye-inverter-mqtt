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


class DeyeSbfSpotMQTTPublisher(DeyeEventProcessor):
    """
    Publishes events to MQTT in sbfSpot json format
    """

    __names={
        "day_energy": "EToday",
        "total_energy": "ETotal",
        "ac/l1/voltage": "UAC1",
        "ac/l1/current": "IAC1",
        "ac/l1/power": "PAC1",
        "ac/freq": "GridFreq",
        "dc/pv1/voltage": "UDC1",
        "dc/pv1/current": "IDC1",
        "dc/pv1/power": "PDC1",
        "dc/pv2/voltage": "UDC2",
        "dc/pv2/current": "IDC2",
        "dc/pv2/power": "PDC2",
        "dc/pv3/voltage": "UDC3",
        "dc/pv3/current": "IDC3",
        "dc/pv3/power": "PDC3",
        "dc/pv4/voltage": "UDC4",
        "dc/pv4/current": "IDC4",
        "dc/pv4/power": "PDC4",
        "dc/total_power": "PDCTot",
        "radiator_temp": "InvTemperature",
    }

    def __init__(self, config: DeyeConfig, mqtt_client: DeyeMqttClient):
        """Initializes the plugin

        Args:
            config (DeyeConfig): provides access to general config
            mqtt_client (DeyeMqttClient): provides access to existing mqtt client (if configured)
        """
        self.__log = logging.getLogger(DeyeSbfSpotMQTTPublisher.__name__)
        self.__config = config

        # change target mqtt topic here
        self.__sbfspot_mqtt_topic = f"{config.mqtt.topic_prefix}/sbfspot/report/Deye-SUN600"

        if mqtt_client is not None:
            self.__mqtt_client = mqtt_client
        else:
            self.__log.error("No mqtt client defined - enable it in config file")


    def get_id(self):
        return "sbfSpot_mqtt_publisher"


    def process(self, events: list[DeyeEvent]):
        now = datetime.now()

        data = {
            "InvClass"  : "Deye",
            "InvType": "SUN600",
            "InvSerial": self.__config.logger.serial_number,
            "Timestamp": str(now.strftime("%m/%d/%Y, %H:%M:%S")),
        }
        #
        # Todo: format floats "{:.2f}".format(3.1415926)

        for event in events:
            if isinstance(event, DeyeObservationEvent):
                data.update(self.__handle_observation(event.observation))
            elif isinstance(event, DeyeLoggerStatusEvent):
                data.update({"InvStatus": "Online" if event.online else "Offline"})
            else:
                self.__log.warn(f"Unsupported event type {event.__class__}")

        self.__log.debug(json.dumps(data))
        # this is still a hack to access existing mqtt client
        self.__mqtt_client._DeyeMqttClient__do_publish(mqtt_topic=self.__sbfspot_mqtt_topic,
                                                       value=json.dumps(data))


    def __handle_observation(self, observation: Observation) -> dict[str, str | float | int]:

        data = {}

        name = DeyeSbfSpotMQTTPublisher.__names.get(observation.sensor.mqtt_topic_suffix)
        if name is not None:
            data[name]=observation.value
        else:
            self.__log.warn("Unknown sbfSpot parameter: name {} mqtt topic {}".format(
                observation.sensor.name,
                observation.sensor.mqtt_topic_suffix))
            data["W-{}".format(observation.sensor.mqtt_topic_suffix)]=observation.value

        return data


class DeyePlugin:
    def __init__(self, plugin_context: DeyePluginContext):
        self.publisher = DeyeSbfSpotMQTTPublisher(config=plugin_context.config,
                                                  mqtt_client=plugin_context.mqtt_client)


    def get_event_processors(self) -> [DeyeEventProcessor]:
        return [self.publisher]
