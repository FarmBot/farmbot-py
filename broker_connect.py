import json
import time

from datetime import datetime
import paho.mqtt.client as mqtt

class BrokerConnect():
    def __init__(self):
        self.token = None
        self.client = None

        self.last_message = None

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

    # def on_connect(self, *_args):
    #     # Subscribe to all channels
    #     self.client.subscribe(f"bot/{self.token['token']['unencoded']['bot']}/#")

    # def on_message(self, _client, _userdata, msg):
    #     print('-' * 100)
    #     # print channel
    #     print(f'{msg.topic} ({datetime.now().strftime("%Y-%m-%d %H:%M:%S")})\n')
    #     # print message
    #     print(json.dumps(json.loads(msg.payload), indent=4))

    # def listen(self):
    #     if self.client is None:
    #         self.connect()

    #     self.client.on_connect = self.on_connect
    #     self.client.on_message = self.on_message

    #     # Start loop in a separate thread
    #     self.client.loop_start()

    #     # Sleep for five seconds to listen for messages
    #     time.sleep(5)

    #     # Stop loop and disconnect after five seconds
    #     self.client.loop_stop()
    #     self.client.disconnect()

    def on_connect(self, _client, _userdata, _flags, _rc, channel):
        # Subscribe to specified channel
        self.client.subscribe(f"bot/{self.token['token']['unencoded']['bot']}/{channel}")

    def on_message(self, _client, _userdata, msg):
        message = json.loads(msg.payload)

        self.last_message = message  # Update last_message

    def listen(self, duration, channel='#'):
        if self.client is None:
            self.connect()

        # Wrap on_connect and on_message methods to pass channel argument
        self.client.on_connect = lambda client, userdata, flags, rc: self.on_connect(client, userdata, flags, rc, channel)
        self.client.on_message = self.on_message

        self.client.loop_start()

        # Listen to messages for duration (seconds)
        time.sleep(duration)

        self.client.loop_stop()
        self.client.disconnect()
