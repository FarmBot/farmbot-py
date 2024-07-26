import threading
import json
import time

from datetime import datetime
import paho.mqtt.client as mqtt

class BrokerConnect():
    def __init__(self):
        self.token = None
        self.client = None

        self.last_message = None

    ## ERROR HANDLING

    ## FUNCTIONS -- SENDING MESSAGES

    def connect(self):
        """Establish persistent connection with message broker."""

        self.client = mqtt.Client()
        self.client.username_pw_set(
            username=self.token['token']['unencoded']['bot'],
            password=self.token['token']['encoded']
        )

        self.client.connect(
            self.token['token']['unencoded']['mqtt'],
            port=1883,
            keepalive=60
        )

        self.client.loop_start()

    def disconnect(self):
        """Disconnect from the message broker."""

        if self.client is not None:
            self.client.loop_stop()
            self.client.disconnect()

    def publish(self, message):
        """Send Celery Script messages via message broker."""

        if self.client is None:
            self.connect()

        self.client.publish(
            f'bot/{self.token["token"]["unencoded"]["bot"]}/from_clients',
            payload=json.dumps(message)
        )

    ## FUNCTIONS -- RECEIVING MESSAGES

    def on_connect(self, _client, _userdata, _flags, _rc, channel):
        """Subscribe to specified broker response channel."""
        self.client.subscribe(f"bot/{self.token['token']['unencoded']['bot']}/{channel}")

    def on_message(self, _client, _userdata, msg):
        """Update message queue with latest broker response."""
        self.last_message = json.loads(msg.payload)

    def show_connect(self, client, *_args):
        # Subscribe to all channels
        client.subscribe(f"bot/{self.token['token']['unencoded']['bot']}/#")

    def show_message(self, _client, _userdata, msg):
        self.last_message = msg.payload
        print('-' * 100)
        # Print channel
        print(f'{msg.topic} ({datetime.now().strftime("%Y-%m-%d %H:%M:%S")})\n')
        # Print message
        print(json.dumps(json.loads(msg.payload), indent=4))

    def listen(self, duration, channel):
        """Listen to messages via message broker."""

        if self.client is None:
            self.connect()

        # Wrap on_connect to pass channel argument
        self.client.on_connect = lambda client, userdata, flags, rc: self.on_connect(client, userdata, flags, rc, channel)
        self.client.on_message = self.on_message

        self.client.loop_start()

        # Listen to messages for duration (seconds)
        time.sleep(duration)

        self.client.loop_stop()
        self.client.disconnect()

    def start_listening(self):
        print("Now listening to message broker...")

        if self.client is None:
            self.connect()

        # Wrap on_connect to pass channel argument
        self.client.on_connect = self.show_connect
        self.client.on_message = self.show_message

        self.client.loop_start()

    def stop_listening(self):
        print("Stopped listening to message broker...")

        self.client.loop_stop()
        self.client.disconnect()
