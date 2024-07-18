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

        new_message = json.loads(msg.payload)
        self.last_message = new_message

    def listen(self, duration, channel='#'):
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
