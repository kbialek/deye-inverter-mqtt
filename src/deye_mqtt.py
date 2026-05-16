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
import ssl
import threading
import json

import paho.mqtt.client as paho

from deye_config import DeyeConfig, ParameterizedLogger
from deye_observation import Observation

import time


class DeyeMqttPublishError(Exception):
    def __init__(self, message: str):
        self.message = message


class DeyeMqttClient:
    def __init__(self, config: DeyeConfig):
        self.__log = logging.getLogger(DeyeMqttClient.__name__)
        self.__mqtt_client = paho.Client(
            client_id=f"deye-inverter-{config.logger.serial_number}",
            reconnect_on_failure=True,
            clean_session=True
        )
        self.__mqtt_client.enable_logger()  # Keep this for paho's internal logging
        if config.mqtt.tls.enabled:
            if config.mqtt.tls.insecure:
                self.__mqtt_client.tls_set(cert_reqs=ssl.CERT_NONE)
                self.__mqtt_client.tls_insecure_set(True)
                self.__log.info(
                    "Enabled TLS encryption for MQTT Broker connection without certificate verification (insecure)"
                )
            else:
                self.__mqtt_client.tls_set(
                    ca_certs=config.mqtt.tls.ca_cert_path,
                    certfile=config.mqtt.tls.client_cert_path,
                    keyfile=config.mqtt.tls.client_key_path,
                )
                self.__log.info("Enabled TLS encryption for MQTT Broker connection with certificate verification")
        if config.mqtt.username and config.mqtt.password:
            self.__mqtt_client.username_pw_set(username=config.mqtt.username, password=config.mqtt.password)
        self.__status_topic = f"{config.mqtt.topic_prefix}/{config.mqtt.availability_topic}"
        self.__mqtt_client.will_set(self.__status_topic, "offline", retain=True, qos=1)
        # Assigning callbacks
        self.__mqtt_client.on_connect = self.__on_connect
        self.__mqtt_client.on_disconnect = self.__on_disconnect_legacy
        self.__config = config.mqtt
        self.__mqtt_timeout = 3  # seconds for publish wait
        self.__publish_lock = threading.RLock()
        self.__command_handlers = {}
        self.__pending_subscriptions = []  # Queue for subscriptions that need to be made after connection
        self.__connection_successful = False  # Flag to track actual successful connection
        self.__loop_started = False

    def subscribe(self, topic: str, callback):
        """Queues a subscription.
        The actual subscription will be made once a connection is successfully established.
        """
        self.__log.debug("Queuing subscription for topic: %s", topic)
        self.__pending_subscriptions.append((topic, callback))
        # If already connected and successful, attempt to subscribe immediately
        if self.__connection_successful:
            self._perform_subscription(topic, callback)

    def _perform_subscription(self, topic: str, callback):
        """  Performs the actual MQTT subscription. Assumes connection is already established.   """
        self.__log.info("Subscribing to topic: %s", topic)
        result, mid = self.__mqtt_client.subscribe(topic, qos=1)
        if result != paho.MQTT_ERR_SUCCESS:
            self.__log.error("Failed to subscribe to topic %s. Return code: %s", topic, result)
        else:
            self.__mqtt_client.message_callback_add(topic, callback)  # Add specific topic callback

    def connect(self) -> bool:
        """Attempts to connect to the MQTT broker.
        Returns True if connection is established, False otherwise.
        """
        if self.__mqtt_client.is_connected() and self.__connection_successful:
            self.__log.debug("MQTT client is already successfully connected.")
            return True
        elif self.__mqtt_client.is_connected() and not self.__connection_successful:
            self.__log.warning(
                "MQTT client appears connected but reported a previous connection failure. "
                "Reconnecting."
            )
            self.disconnect()  # Force a clean disconnect to re-attempt connection
        self.__log.info("Attempting to connect to MQTT Broker at %s:%d...", self.__config.host, self.__config.port)
        try:
            self.__mqtt_client.connect(self.__config.host, self.__config.port, keepalive=60)
            self.__mqtt_client.loop_start()  # Start network loop
            # Wait for connection to establish or fail
            start_time = time.time()
            # Maximum wait time for connection attempt
            connection_timeout = 10  # seconds
            if not self.__loop_started:
                self.__mqtt_client.connect(self.__config.host, self.__config.port, keepalive=60)
                self.__mqtt_client.loop_start()
                self.__loop_started = True
            while not self.__mqtt_client.is_connected():
                if time.time() - start_time > connection_timeout:
                    self.__log.error("Connection attempt timed out after %d seconds.", connection_timeout)
                    return False
                time.sleep(0.1)  # Small delay to prevent busy-waiting
            # After the loop, check the success flag set by __on_connect
            if self.__connection_successful:
                self.__log.info("MQTT connection established.")
                # Process any pending subscriptions now that we are connected
                self._process_pending_subscriptions()
                return True
            else:
                # If on_connect didn't set the flag, it means connection failed for other reasons (auth, etc.)
                # The specific error should have been logged by __on_connect
                self.__log.error("MQTT connection failed (check logs for details).")
                return False
        except ConnectionRefusedError:
            self.__log.error(
                "Connection refused. Make sure the MQTT broker is running at %s:%d.",
                self.__config.host,
                self.__config.port
            )
            return False
        except OSError as e:
            self.__log.error("OS error during MQTT connection to %s:%d: %s", self.__config.host, self.__config.port, e)
            return False
        except Exception as e:
            self.__log.error("An unexpected error occurred during MQTT connection: %s", e)
            return False

    def __on_connect(self, client, userdata, flags, rc) -> None:
        """Callback function for when the client connects to the MQTT broker.
        Handles different return codes to provide specific error messages.
        """
        self.__connection_successful = False  # Reset flag for each connect attempt
        if rc == 0:
            self.__connection_successful = True
            self.__log.info(
                "Successfully connected to MQTT Broker located at %s:%d",
                self.__config.host,
                self.__config.port
            )
            # Publish online status
            self.__mqtt_client.publish(self.__status_topic, "online", retain=True, qos=1)
            # Resubscribe to command handlers (these are assumed to be essential)
            self.__resubscribe_command_handlers()
            # Process any subscriptions that were queued while disconnected
            self._process_pending_subscriptions()
        elif rc == 1:
            self.__log.error("Connection error: Protocol error")
        elif rc == 2:
            self.__log.error("Connection error: Invalid client ID")
        elif rc == 3:
            self.__log.error("Connection error: Server unavailable")
        elif rc == 4:
            self.__log.error("Connection error: Bad username or password")
        elif rc == 5:
            self.__log.error("Connection error: Not authorized")
        else:
            self.__log.error("Connection error: Unknown error, return code: %d", rc)
        # If connection failed, ensure the flag is false. The loop_start should handle reconnections.
        if not self.__connection_successful:
            self.__log.warning("MQTT connection failed. Attempting to reconnect...")

    def __on_disconnect(self, client, userdata, rc, properties=None) -> None:  # v2 callback signature
        """Callback function for when the client disconnects from the MQTT broker (VERSION2 API)."""
        self.__connection_successful = False  # Connection lost
        if rc != 0:
            self.__log.warning(
                f"Disconnected from MQTT Broker unexpectedly. Reason code: {rc}"
            )
        else:
            self.__log.info("Disconnected from MQTT Broker gracefully.")
        # The loop_start() method should handle reconnections automatically.

    def __on_disconnect_legacy(self, client, userdata, rc) -> None:  # Legacy callback signature
        """Callback function for when the client disconnects from the MQTT broker (Legacy API)."""
        self.__connection_successful = False  # Connection lost
        if rc != 0:
            self.__log.warning(
                f"Disconnected from MQTT Broker unexpectedly. Reason code: {rc}"
            )
        else:
            self.__log.info("Disconnected from MQTT Broker gracefully.")
        # The loop_start() method should handle reconnections automatically.

    def _process_pending_subscriptions(self):
        """Processes any subscriptions that were queued while the client was disconnected.
        This is called automatically when a successful connection is made.
        """
        if self.__pending_subscriptions:
            self.__log.debug(
                "Processing %d pending subscriptions.",
                len(self.__pending_subscriptions)
            )
            subscriptions = self.__mqtt_client.get_subscriptions()
            for topic, callback in list(self.__pending_subscriptions):
                # Check if it's already subscribed to prevent duplicates if connection is unstable
                if topic not in subscriptions:  # paho doesn't expose this easily
                    self._perform_subscription(topic, callback)
            # Remove from pending if successful, or keep if there was an error.
            # For now, we'll clear the whole list if all attempts succeed.
            # Clear pending subscriptions after attempting to process them
            # If _perform_subscription fails for some, they will be re-queued on next connect.
            self.__pending_subscriptions.clear()

    def __resubscribe_command_handlers(self):
        """Resubscribes to all command topics when a connection is established."""
        for mqtt_topic, handler_method in list(self.__command_handlers.items()):
            self.__log.debug("Resubscribing to command topic: %s", mqtt_topic)
            self._perform_subscription(mqtt_topic, handler_method)

    def disconnect(self):
        self.__log.info("Disconnecting from MQTT Broker...")
        if self.__mqtt_client.is_connected():
            self.__mqtt_client.disconnect()
        self.__mqtt_client.loop_stop()  # Stop the network loop
        self.__log.info("MQTT client stopped and disconnected.")

    def publish(self, mqtt_topic: str, value: str):
        """Publishes a message to the given MQTT topic.
        Handles connection and potential publishing errors.
        Ensure we are actually connected and the connection was successful
        """
        if not self.__connection_successful:
            self.__log.warning(
                "Cannot publish message to '%s': Not connected to MQTT broker.",
                mqtt_topic
            )
            return  # Exit if not connected
        try:
            self.__publish_lock.acquire()
            self.__log.debug("Publishing message. topic: '%s', value: '%s'", mqtt_topic, value)
            info = self.__mqtt_client.publish(mqtt_topic, value, qos=1)
            # Wait for publish confirmation, with a timeout
            if info.rc == paho.MQTT_ERR_SUCCESS:
                info.wait_for_publish(self.__mqtt_timeout)
                self.__log.debug("Message published successfully to topic '%s'", mqtt_topic)
            else:
                self.__log.error("Failed to publish message to topic '%s'. Return code: %s", mqtt_topic, info.rc)
                raise DeyeMqttPublishError(f"MQTT publish failed with return code {info.rc}")
        except ValueError as e:
            # This typically means the outgoing queue is full
            self.__log.error("MQTT outgoing queue is full: %s", e)
            raise DeyeMqttPublishError(f"MQTT outgoing queue is full: {str(e)}")
        except RuntimeError as e:
            # Catch other runtime errors during publish
            self.__log.error("Unknown MQTT publishing error: %s", e)
            raise DeyeMqttPublishError(f"Unknown MQTT publishing error: {str(e)}")
        except OSError as e:
            # This can happen if the connection is lost during the publish attempt
            self.__log.error("MQTT connection error during publish to %s: %s", mqtt_topic, e)
            raise DeyeMqttPublishError(f"MQTT connection error during publish: {str(e)}")
        except Exception as e:
            # Catch any other unexpected errors
            self.__log.error("An unexpected error occurred during MQTT publish to %s: %s", mqtt_topic, e)
            raise DeyeMqttPublishError(f"Unexpected MQTT publishing error: {str(e)}")
        finally:
            self.__publish_lock.release()

    def __build_topic_name(self, logger_topic_prefix: str, topic_suffix: str) -> str:
        """Internal helper to construct a full MQTT topic."""
        if logger_topic_prefix:
            return f"{self.__config.topic_prefix}/{logger_topic_prefix}/{topic_suffix}"
        else:
            return f"{self.__config.topic_prefix}/{topic_suffix}"

    def __map_logger_index_to_topic_prefix(self, logger_index: int):
        """Maps a logger index to a topic prefix, handling the case where index is 0."""
        return str(logger_index) if logger_index > 0 else ""

    def build_topic_name(self, logger_index: int, topic_suffix: str) -> str:
        """ Builds a full MQTT topic name based on configuration, logger index, and topic suffix.
        Example: topic_prefix/logger_index/topic_suffix
        If logger_index is 0, it becomes: topic_prefix/topic_suffix """
        logger_topic_prefix = self.__map_logger_index_to_topic_prefix(logger_index)
        return self.__build_topic_name(logger_topic_prefix, topic_suffix)

    def publish_observation(self, observation: Observation, logger_index: int):
        """ Publishes an observation to its corresponding MQTT topic. """
        if observation.sensor.mqtt_topic_suffix:
            mqtt_topic = self.build_topic_name(logger_index, observation.sensor.mqtt_topic_suffix)
            value = observation.value_as_str()
            try:
                self.publish(mqtt_topic, value)
            except DeyeMqttPublishError as e:
                self.__log.error("Failed to publish observation for %s: %s", observation.sensor.name, e.message)
        else:
            self.__log.debug(
                "No MQTT topic suffix configured for sensor '%s', skipping publish.",
                observation.sensor.name
            )

    def publish_logger_status(self, is_online: bool, logger_index: int):
        """Publishes the online/offline status of a logger to its status topic."""
        mqtt_topic = self.build_topic_name(logger_index, self.__config.logger_status_topic)
        value = "online" if is_online else "offline"
        try:
            self.publish(mqtt_topic, value)
            ParameterizedLogger(self.__log, logger_index).info("Logger is %s", value)
        except DeyeMqttPublishError as e:
            ParameterizedLogger(self.__log, logger_index).error("Failed to publish logger status: %s", e.message)

    # --- New method to handle incoming messages for Deye inverter data ---
    def __process_deye_data(self, client, userdata, msg):
        """ Callback function for when a message is received on a subscribed topic.
        This function should parse the Deye inverter data and process it. """
        self.__log.debug(f"Received raw message on topic '{msg.topic}': {msg.payload.decode()}")
        try:
            # Assuming the payload is JSON data from the Deye inverter
            data = json.loads(msg.payload.decode())
            # You need to implement the actual processing of Deye data here.
            # This is a placeholder, you'll likely want to pass this to another
            # class or function that handles the inverter data.
            self.__log.info("Processing Deye data from topic '%s'", msg.topic)
            # Example: print some common fields if they exist
            if "serial_number" in data:
                self.__log.info(f"  Serial Number: {data['serial_number']}")
            if "active_power" in data:
                self.__log.info(f"  Active Power: {data['active_power']} W")
            # Add more processing logic here based on your needs...
        except json.JSONDecodeError:
            self.__log.error("Error: Received payload on topic '%s' is not valid JSON.", msg.topic)
        except Exception as e:
            self.__log.error("Error processing received message on topic '%s': %s", msg.topic, e)

    def setup_deye_data_subscription(self, deye_data_topic: str):
        """Sets up the subscription for Deye inverter data messages.
        The actual subscription is queued and performed upon successful connection.
        The topic might be absolute or relative to topic_prefix.
        If it doesn't start with '/', assume it's relative and prepend topic_prefix.
        """
        if not deye_data_topic.startswith('/'):
            full_topic = f"{self.__config.topic_prefix}/{deye_data_topic}"
        else:
            full_topic = deye_data_topic  # Assume it's an absolute topic
        # Use a lambda to pass the client and any necessary context to the callback
        # The subscription itself is queued by the 'subscribe' method.
        self.subscribe(full_topic, lambda client, userdata, msg: self.__process_deye_data(client, userdata, msg))

    def extract_command_topic_suffix(self, logger_index: int, topic: str) -> str | None:
        """Extracts the command suffix from an incoming MQTT topic, if it matches the expected pattern.
        Returns the extracted suffix or None if the topic does not match.
        """
        logger_topic_prefix = self.__map_logger_index_to_topic_prefix(logger_index)
        prefix = f"{self.__config.topic_prefix}/"
        if logger_topic_prefix:
            prefix = f"{prefix}{logger_topic_prefix}/"
        suffix = "/command"
        # Ensure the topic starts with the expected prefix and ends with the command suffix
        if topic.startswith(prefix) and topic.endswith(suffix):
            # Extract the part between the prefix and the suffix
            command_suffix = topic[len(prefix):-len(suffix)]
            return command_suffix
        else:
            return None

    def subscribe_command_handler(self, logger_index: int, mqtt_topic_suffix: str, handler_method):
        """  Subscribes to a specific command topic and registers a handler for it.
        The subscription is queued. """
        mqtt_topic = self.build_topic_name(logger_index, f"{mqtt_topic_suffix}/command")
        # Store the handler in our internal dictionary for resubscription on reconnect
        self.__command_handlers[mqtt_topic] = handler_method
        # Queue the subscription to be performed once connected
        self.subscribe(mqtt_topic, handler_method)
