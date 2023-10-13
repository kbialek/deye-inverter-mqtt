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
import json
from deye_config import DeyeConfig
from deye_mqtt import DeyeMqttClient, DeyeMqttPublishError
from deye_plugin_loader import DeyePluginContext
from deye_events import DeyeEventProcessor, DeyeEvent, DeyeObservationEvent

from deye_sensor import SingleRegisterSensor
from deye_sensors import sensor_list

    
class MqttAutoConfPublisher(DeyeMqttClient):
    def __init__(self, config: DeyeConfig):
        super().__init__(config)

    def __do_publish(self, mqtt_topic: str, value: str):
        try:
            info = self._mqtt_client.publish(mqtt_topic, value, qos=1)
            info.wait_for_publish(1)
        except ValueError as e:
            raise DeyeMqttPublishError(f"MQTT outgoing queue is full: {str(e)}")
        except RuntimeError as e:
            raise DeyeMqttPublishError(f"Unknown MQTT publishing error: {str(e)}")
        except OSError as e:
            raise DeyeMqttPublishError(f"MQTT connection error: {str(e)}")

    def publish_sensor(self, topic: str, value: str):
        self.__do_publish(topic, value)
        #self._log.info("Logger is %s", value)



class DeyePlugin:
    """Plugin entrypoint

    The plugin loader first instantiates DeyePlugin class, and then gets event processors from it. 
    """
    def __init__(self, plugin_context: DeyePluginContext):
        """Initializes the plugin

        Args:
            plugin_context (DeyePluginContext): provides access to core service components, e.g. config
        """
        

        self.config = plugin_context.config
        self.sensors = sensor_list
        self.mqtt_client = MqttAutoConfPublisher(plugin_context.config)
        self.mqtt_client.connect()
        for sensor in self.sensors:
            self.__configure_sensors(sensor)
        self.mqtt_client.disconnect()

    def get_event_processors(self) -> [DeyeEventProcessor]:
        """We dont need to process events, so we return an empty list 
        """
        return []
    
    def __configure_sensors(self, sensor: SingleRegisterSensor) -> [DeyeEventProcessor]:
        """Create a Home Assistant MQTT auto discovery configuration for a sensor 
        """
        unique_id = f"deye_{self.config.logger.serial_number}_{sensor.mqtt_topic_suffix.replace('/', '' )}"
        mqtt_topic = f"homeassistant/sensor/{unique_id}/config"
        ha_config = {
            'device_class': f"{sensor.device_class}",
            'name': f"{sensor.name}",
            'state_topic': f"{self.config.mqtt.topic_prefix}/{sensor.mqtt_topic_suffix}",
            'unit_of_measurement': f"{sensor.unit}",
            'unique_id': f"{unique_id}",
            'device': {
                'identifiers': [f"deye{self.config.logger.serial_number}"],
                'name': f"Deye {self.config.logger.serial_number}"
            }
        }
        self.mqtt_client.publish_sensor(topic=mqtt_topic, value=json.dumps(ha_config))
        return self.sensors
