"""
BrokerConnect class.
"""

# └── functions/broker.py
#     ├── [BROKER] connect()
#     ├── [BROKER] disconnect()
#     ├── [BROKER] publish()
#     ├── [BROKER] start_listen()
#     ├── [BROKER] stop_listen()
#     └── [BROKER] listen()

import time
import json
import uuid
from datetime import datetime
import paho.mqtt.client as mqtt

class BrokerConnect():
    """Broker connection class."""
    def __init__(self, state):
        self.state = state
        self.client = None

    def connect(self):
        """Establish persistent connection to send messages via message broker."""

        self.state.check_token()

        self.client = mqtt.Client()
        self.client.username_pw_set(
            username=self.state.token["token"]["unencoded"]["bot"],
            password=self.state.token["token"]["encoded"]
        )

        self.client.connect(
            self.state.token["token"]["unencoded"]["mqtt"],
            port=1883,
            keepalive=60
        )

        self.client.loop_start()

        self.state.print_status(description="Connected to message broker.")

    def disconnect(self):
        """Disconnect from the message broker."""

        if self.client is not None:
            self.client.loop_stop()
            self.client.disconnect()
            self.state.print_status(description="Disconnected from message broker.")

    def wrap_message(self, message, priority=None):
        """Wrap message in CeleryScript format."""
        rpc = {
            "kind": "rpc_request",
            "args": {
                "label": "",
            },
            "body": [message],
        }

        if priority is not None:
            rpc["args"]["priority"] = priority

        return rpc

    def publish(self, message):
        """Publish messages containing CeleryScript via the message broker."""

        if self.client is None:
            self.connect()

        rpc = message
        if rpc["kind"] != "rpc_request":
            rpc = self.wrap_message(rpc)

        if rpc["args"]["label"] == "":
            rpc["args"]["label"] = uuid.uuid4().hex if not self.state.test_env else "test"

        self.state.print_status(description="Publishing to 'from_clients':")
        self.state.print_status(endpoint_json=rpc, update_only=True)
        if self.state.dry_run:
            self.state.print_status(description="Sending disabled, message not sent.", update_only=True)
        else:
            self.listen("from_device", publish_payload=rpc)

        response = self.state.last_messages.get("from_device")
        if response is not None:
            if response["kind"] == "rpc_ok":
                self.state.print_status(description="Success response received.", update_only=True)
                self.state.error = None
            else:
                self.state.print_status(description="Error response received.", update_only=True)
                self.state.error = "RPC error response received."

        self.state.last_published = rpc

    def start_listen(self, channel="#"):
        """Establish persistent subscription to message broker channels."""

        if self.client is None:
            self.connect()

        # Set on_message callback
        def on_message(_client, _userdata, msg):
            """on_message callback"""

            self.state.last_messages[channel] = json.loads(msg.payload)


            self.state.print_status(description="", update_only=True)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.state.print_status(
                endpoint_json=json.loads(msg.payload),
                description=f"TOPIC: {msg.topic} ({timestamp})\n")

        self.client.on_message = on_message

        # Subscribe to channel
        device_id_str = self.state.token["token"]["unencoded"]["bot"]
        self.client.subscribe(f"bot/{device_id_str}/{channel}")
        self.state.print_status(description=f"Connected to message broker channel '{channel}'")

        # Start listening
        self.client.loop_start()
        self.state.print_status(description=f"Now listening to message broker channel '{channel}'.")

    def stop_listen(self):
        """End subscription to all message broker channels."""

        self.client.loop_stop()

        self.state.print_status(description="Stopped listening to all message broker channels.")

    def listen(self, channel, duration=None, publish_payload=None):
        """Listen to a message broker channel for the provided duration in seconds."""
        # Prepare parameters
        duration_seconds = duration or self.state.broker_listen_duration
        message = (publish_payload or {}).get("body", [{}])[0]
        if message.get("kind") == "wait":
            duration_seconds += message["args"]["milliseconds"] / 1000
        publish = publish_payload is not None
        label = None
        if publish and publish_payload["args"]["label"] != "":
            label = publish_payload["args"]["label"]

        # Print status message
        channel_str = f" channel '{channel}'" if channel != "#" else ""
        duration_str = f" for {duration_seconds} seconds"
        label_str = f" for label '{label}'" if label is not None else ""
        description = f"Listening to message broker{channel_str}{duration_str}{label_str}..."
        self.state.print_status(description=description)

        # Start listening
        start_time = datetime.now()
        self.start_listen(channel)
        if not self.state.test_env:
            self.state.last_messages[channel] = None
        if publish:
            time.sleep(0.1) # wait for start_listen to be ready
            device_id_str = self.state.token["token"]["unencoded"]["bot"]
            publish_topic =  f"bot/{device_id_str}/from_clients"
            self.client.publish(publish_topic, payload=json.dumps(publish_payload))
        self.state.print_status(update_only=True, description="", end="")
        while (datetime.now() - start_time).seconds < duration_seconds:
            self.state.print_status(update_only=True, description=".", end="")
            time.sleep(0.25)
            last_message = self.state.last_messages.get(channel)
            if last_message is not None:
                # If a label is provided, verify the label matches
                if label is not None and last_message["args"]["label"] != label:
                    self.state.last_messages[channel] = None
                    continue
                seconds = (datetime.now() - start_time).seconds
                self.state.print_status(description="", update_only=True)
                self.state.print_status(
                    description=f"Message received after {seconds} seconds",
                    update_only=True)
                break
        if self.state.last_messages.get(channel) is None:
            self.state.print_status(description="", update_only=True)
            self.state.print_status(
                description=f"Did not receive message after {duration_seconds} seconds",
                update_only=True)
            self.state.error = "Timed out waiting for RPC response."

        self.stop_listen()
