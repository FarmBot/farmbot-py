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
import math
import json
import uuid
import functools
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
            description = "Disconnected from message broker."
            self.state.print_status(description=description)

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
            if self.state.test_env:
                rpc["args"]["label"] = "test"
            else:
                rpc["args"]["label"] = uuid.uuid4().hex

        self.state.print_status(description="Publishing to 'from_clients'")
        self.state.print_status(endpoint_json=rpc, update_only=True)
        if self.state.dry_run:
            self.state.print_status(
                description="Sending disabled, message not sent.",
                update_only=True)
        else:
            self.listen("from_device", publish_payload=rpc)

        response = self.state.last_messages.get("from_device", [])
        if len(response) > 0:
            if response[-1]["kind"] == "rpc_ok":
                self.state.print_status(
                    description="Success response received.",
                    update_only=True)
                self.state.error = None
            else:
                self.state.print_status(
                    description="Error response received.",
                    update_only=True)
                self.state.error = "RPC error response received."

        self.state.last_published = rpc

    def start_listen(self, channel="#", message_options=None):
        """Establish persistent subscription to message broker channels."""
        options = message_options or {}
        path = (options.get("path", "") or "").split(".") or []
        path = [key for key in path if key != ""]
        diff_only = options.get("diff_only")

        if self.client is None:
            self.connect()

        def add_message(key, value):
            """Add message to last_messages."""
            if key not in self.state.last_messages:
                self.state.last_messages[key] = []
            self.state.last_messages[key].append(value)

        # Set on_message callback
        def on_message(_client, _userdata, msg):
            """on_message callback"""
            channel_key = msg.topic.split("/")[-1]
            payload = json.loads(msg.payload)

            if channel == "#":
                add_message(channel, payload)
            add_message(channel_key, payload)

            for key in path:
                payload = payload[key]
            path_channel = f"{channel_key}_excerpt"
            add_message(path_channel, payload)

            if diff_only:
                diff = payload
                key = path_channel if len(path) > 0 else channel_key
                last_messages = self.state.last_messages.get(key, [])
                if len(last_messages) > 1:
                    current = last_messages[-1]
                    previous = last_messages[-2]
                    diff, _is_different = difference(current, previous)
                payload = diff
                add_message(f"{channel_key}_diffs", payload)

            self.state.print_status(description="", update_only=True)
            description = "New message"
            if len(path) > 0:
                description += f" {'.'.join(path)}"
            if diff_only:
                description += " diff"
            description += f" from {msg.topic}"
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            description += f" ({timestamp})"
            self.state.print_status(
                endpoint_json=payload,
                description=description)

        self.client.on_message = on_message

        # Subscribe to channel
        device_id_str = self.state.token["token"]["unencoded"]["bot"]
        self.client.subscribe(f"bot/{device_id_str}/{channel}")
        description = f"Connected to message broker channel '{channel}'"
        if channel == "#":
            description = "Connected to all message broker channels"
        self.state.print_status(description=description)

        # Start listening
        self.client.loop_start()
        description = f"Now listening to message broker channel '{channel}'"
        if channel == "#":
            description = "Now listening to all message broker channels"
        self.state.print_status(description=description)

    def stop_listen(self):
        """End subscription to all message broker channels."""

        self.client.loop_stop()

        self.state.print_status(
            description="Stopped listening to all message broker channels.")

    @staticmethod
    def stop_listen_upon_interrupt(func):
        """Decorator to stop listening upon KeyboardInterrupt."""
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            try:
                func(self, *args, **kwargs)
            except KeyboardInterrupt:
                self.stop_listen()
        return wrapper

    @stop_listen_upon_interrupt
    def listen(self,
               channel="#",
               duration=None,
               publish_payload=None,
               stop_count=1,
               message_options=None):
        """Listen to a message broker channel for the provided duration in seconds."""
        publish = publish_payload is not None
        message = (publish_payload or {}).get("body", [{}])[0]
        # Prepare duration option
        timeout_key = "listen"
        if message.get("kind") in ["move", "find_home", "calibrate"]:
            timeout_key = "movements"
        duration_seconds = duration or self.state.timeout[timeout_key]
        if message.get("kind") == "wait":
            duration_seconds += message["args"]["milliseconds"] / 1000
        if stop_count > 1:
            duration_seconds = math.inf
        # Prepare label option
        label = None
        if publish and publish_payload["args"]["label"] != "":
            label = publish_payload["args"]["label"]
        if message.get("kind") == "read_status":
            # Getting the RPC response to read_status isn't as important as
            # returning the status as soon as possible, since the device
            # will still publish a status within a few seconds even if the
            # read_status command isn't received.
            channel = "status"
            label = None

        # Print status message
        description = "Listening to message broker"
        if channel != "#":
            description += f" channel '{channel}'"
        if duration_seconds != math.inf:
            description += f" for {duration_seconds} seconds"
        if label is not None:
            description += f" for label '{label}'"
        plural = "s are" if stop_count > 1 else " is"
        description += f" until {stop_count} message{plural} received"
        description += "..."
        self.state.print_status(description=description)

        # Start listening
        start_time = datetime.now()
        self.start_listen(channel, message_options)
        if not self.state.test_env:
            if channel == "#":
                self.state.last_messages = {"#": []}
            else:
                self.state.last_messages[channel] = []
        if publish:
            time.sleep(0.1)  # wait for start_listen to be ready
            device_id_str = self.state.token["token"]["unencoded"]["bot"]
            publish_topic = f"bot/{device_id_str}/from_clients"
            self.client.publish(
                publish_topic,
                payload=json.dumps(publish_payload))
        self.state.print_status(update_only=True, description="", end="")
        while (datetime.now() - start_time).seconds < duration_seconds:
            self.state.print_status(update_only=True, description=".", end="")
            time.sleep(0.25)
            last_messages = self.state.last_messages.get(channel, [])
            if len(last_messages) > 0:
                # If a label is provided, verify the label matches
                if label is not None and last_messages[-1]["args"]["label"] != label:
                    self.state.last_messages[channel] = []
                    continue
                if len(last_messages) > (stop_count - 1):
                    seconds = (datetime.now() - start_time).seconds
                    prefix = f"{stop_count} messages"
                    if stop_count == 1:
                        prefix = "Message"
                    description = f"{prefix} received after {seconds} seconds"
                    self.state.print_status(
                        description=description,
                        update_only=True)
                    break
        if len(self.state.last_messages.get(channel, [])) == 0:
            self.state.print_status(description="", update_only=True)
            secs = duration_seconds
            description = f"Did not receive message after {secs} seconds"
            self.state.print_status(
                description=description,
                update_only=True)
            self.state.error = "Timed out waiting for RPC response."
        else:
            self.state.error = None

        self.stop_listen()


def difference(next_state, prev_state):
    """Find the difference between two states."""
    is_different = False
    diff = {}

    for key, next_value in next_state.items():
        if key not in prev_state:
            diff[key] = next_value
            is_different = True
            continue
        prev_value = prev_state[key]
        if next_value != prev_value:
            if isinstance(next_value, dict) and isinstance(prev_value, dict):
                nested_diff, nested_is_different = difference(
                    next_value,
                    prev_value)
                if nested_is_different:
                    diff[key] = nested_diff
                    is_different = True
            else:
                diff[key] = next_value
                is_different = True

    for key in prev_state:
        if key not in next_state:
            is_different = True

    return diff, is_different
