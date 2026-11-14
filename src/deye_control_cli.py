"""MQTT RPC client. Never opens an inverter connection or logs credentials.

Licensed under the Apache License, Version 2.0 (the "License");
http://www.apache.org/licenses/LICENSE-2.0
Distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND.
"""

import argparse
import json
import ssl
import threading
import time
import uuid

import paho.mqtt.client as paho

from deye_config import DeyeMqttConfig


def rpc(operation, body=None, logger_index=0, timeout=8):
    config = DeyeMqttConfig.from_env()
    prefix = config.topic_prefix + (f"/{logger_index}" if logger_index > 0 else "")
    request = {"schema": 1, "request_id": uuid.uuid4().hex, "op": operation, "body": body or {}}
    if operation == "session":
        request["expires_at"] = time.time() + 30
    client = paho.Client(
        client_id="deye-control-cli-" + uuid.uuid4().hex, clean_session=True, reconnect_on_failure=False
    )
    client.max_queued_messages_set(1)
    if config.username:
        client.username_pw_set(config.username, config.password)
    if config.tls.enabled:
        client.tls_set(
            ca_certs=config.tls.ca_cert_path,
            certfile=config.tls.client_cert_path,
            keyfile=config.tls.client_key_path,
            cert_reqs=ssl.CERT_NONE if config.tls.insecure else ssl.CERT_REQUIRED,
        )
        if config.tls.insecure:
            client.tls_insecure_set(True)
    subscribed, received = threading.Event(), threading.Event()
    response = []
    published = False

    def connected(mqtt, userdata, flags, rc):
        if rc == 0:
            mqtt.subscribe(prefix + "/control/result", qos=1)

    def message(mqtt, userdata, msg):
        if msg.retain:
            return
        try:
            value = json.loads(msg.payload)
            if value.get("request_id") == request["request_id"]:
                response.append(value)
                received.set()
        except (ValueError, TypeError, AttributeError):
            return

    client.on_connect = connected
    client.on_subscribe = lambda *args: subscribed.set()
    client.on_message = message
    try:
        client.connect_async(config.host, config.port, keepalive=30)
        client.loop_start()
        if not subscribed.wait(timeout):
            return {"error": "mqtt_unavailable", "uncertain": False}, 1
        payload = json.dumps(request, allow_nan=False)
        info = client.publish(prefix + "/control/request", payload, qos=1, retain=False)
        published = True
        if info.rc != paho.MQTT_ERR_SUCCESS or not received.wait(timeout):
            return {
                "error": "rpc_result_unknown",
                "uncertain": True,
                "request_id": request["request_id"],
                "command_id": request["body"].get("id"),
            }, 1
        value = response[0]
        return (value["result"], 0) if value.get("ok") else ({"error": value.get("error")}, 1)
    except (OSError, ValueError):
        return {"error": "mqtt_client_error", "uncertain": published}, 1
    finally:
        client.disconnect()
        client.loop_stop()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("operation", choices=("status", "preview", "command", "get", "session"))
    parser.add_argument("body", nargs="?", default="{}", help="JSON, or command ID for get")
    parser.add_argument("--logger-index", type=int, default=0)
    args = parser.parse_args()
    body = {"id": args.body} if args.operation == "get" else json.loads(args.body)
    if args.operation == "command":
        body.setdefault("id", uuid.uuid4().hex)
        body.setdefault("expires_at", time.time() + 30)
    result, code = rpc("submit" if args.operation == "command" else args.operation, body, args.logger_index)
    print(json.dumps(result, allow_nan=False))
    raise SystemExit(code)


if __name__ == "__main__":
    main()
