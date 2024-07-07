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

import importlib
import pkgutil
import logging
import sys
import os

from deye_config import DeyeConfig
from deye_mqtt import DeyeMqttClient
from deye_events import DeyeEventProcessor


class DeyePluginContext:
    def __init__(self, config: DeyeConfig, mqtt_client: DeyeMqttClient):
        self.config = config
        self.mqtt_client = mqtt_client


class DeyePluginLoader:
    def __init__(self, config: DeyeConfig):
        self.__log = logging.getLogger(DeyePluginLoader.__name__)
        self.__config = config
        self.__plugins = []

    def load_plugins(self, plugin_context: DeyePluginContext):
        if not os.path.isdir(self.__config.plugins_dir):
            return

        sys.path.append(self.__config.plugins_dir)
        discovered_plugins = {
            name: importlib.import_module(name)
            for finder, name, ispkg in pkgutil.iter_modules(path=[self.__config.plugins_dir])
            if name.startswith("deye_plugin_")
        }

        for plugin_name in discovered_plugins:
            if plugin_name not in self.__config.plugins_enabled:
                self.__log.info(
                    "Plugin '%s' discovered but not loaded, because it's not enabled in the config", plugin_name
                )
                continue

            self.__log.info("Loading plugin: '%s'", plugin_name)
            plugin_module = discovered_plugins[plugin_name]
            try:
                self.__plugins.append(plugin_module.DeyePlugin(plugin_context))
            except AttributeError:
                self.__log.warn("Ignoring plugin '%s', because DeyePlugin class is not defined.", plugin_name)

    def get_event_processors(self) -> [DeyeEventProcessor]:
        event_processors = []
        for plugin in self.__plugins:
            event_processors.extend(plugin.get_event_processors())
        for event_processor in event_processors:
            self.__log.info("Loading custom event processor: '%s'", event_processor.get_id())
        return event_processors
