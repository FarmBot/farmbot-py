"""
BrokerConnect class.
"""

# └── functions/broker.py
#     ├── [BROKER] connect()
#     ├── [BROKER] disconnect()
#     ├── [BROKER] publish()
#     ├── [BROKER] on_connect()
#     ├── [BROKER] on_message
#     ├── [BROKER] start_listen()
#     ├── [BROKER] stop_listen()
#     └── [BROKER] listen()

import time
import json
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
            username=self.state.token['token']['unencoded']['bot'],
            password=self.state.token['token']['encoded']
        )

        self.client.connect(
            self.state.token['token']['unencoded']['mqtt'],
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
            rpc['args']['priority'] = priority

        return rpc

    def publish(self, message):
        """Publish messages containing CeleryScript via the message broker."""

        if self.client is None:
            self.connect()

        if message["kind"] != "rpc_request":
            message = self.wrap_message(message)

        device_id_str = self.state.token["token"]["unencoded"]["bot"]
        topic = f"bot/{device_id_str}/from_clients"
        self.client.publish(topic, payload=json.dumps(message))
        self.state.print_status(description=f"Publishing to {topic}:")
        self.state.print_status(endpoint_json=message, update_only=True)

    def on_connect(self, _client, _userdata, _flags, _rc, channel):
        """Callback function when connection to message broker is successful."""

        self.client.subscribe(
            f"bot/{self.state.token['token']['unencoded']['bot']}/{channel}")

        self.state.print_status(description=f"Connected to message broker channel {channel}")

    def on_message(self, _client, _userdata, msg, channel):
        """Callback function when message received from message broker."""

        self.state.last_messages[channel] = json.loads(msg.payload)

        self.state.print_status(endpoint_json=json.loads(msg.payload), description=f"TOPIC: {msg.topic} ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})\n")

    def start_listen(self, channel="#"):
        """Establish persistent subscription to message broker channels."""

        if self.client is None:
            self.connect()

        def on_connect(client, userdata, flags, rc):
            """Wrap on_connect to pass channel argument."""
            self.on_connect(client, userdata, flags, rc, channel)

        def on_message(client, userdata, msg):
            """Wrap on_message to pass channel argument."""
            self.on_message(client, userdata, msg, channel)

        self.client.on_connect = on_connect
        self.client.on_message = on_message

        self.client.loop_start()
        self.state.print_status(description=f"Now listening to message broker channel {channel}.")

    def stop_listen(self):
        """End subscription to all message broker channels."""

        self.client.loop_stop()
        self.client.disconnect()

        self.state.print_status(description="Stopped listening to all message broker channels.")

    def listen(self, duration, channel):
        """Listen to a message broker channel for the provided duration in seconds."""
        self.state.print_status(description=f"Listening to message broker for {duration} seconds...")
        start_time = datetime.now()
        self.start_listen(channel)
        if not self.state.test_env:
            self.state.last_messages[channel] = None
        while (datetime.now() - start_time).seconds < duration:
            self.state.print_status(update_only=True, description=".", end="")
            time.sleep(0.25)
            if self.state.last_messages.get(channel) is not None:
                seconds = (datetime.now() - start_time).seconds
                self.state.print_status(
                    description=f"Message received after {seconds} seconds",
                    update_only=True)
                break
        if self.state.last_messages.get(channel) is None:
            self.state.print_status(
                description=f"Did not receive message after {duration} seconds",
                update_only=True)

        self.stop_listen()
