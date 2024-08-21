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
#     └── [BROKER] stop_listen()

from .imports import *

class BrokerConnect():
    def __init__(self, state):
        self.state = state
        self.client = None

    def connect(self):
        """Establish persistent connection to send messages via message broker."""

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

    def disconnect(self):
        """Disconnect from the message broker."""

        if self.client is not None:
            self.client.loop_stop()
            self.client.disconnect()

        return

    def publish(self, message):
        """Publish messages containing CeleryScript via the message broker."""

        if self.client is None:
            self.connect()

        self.client.publish(f'bot/{self.state.token["token"]["unencoded"]["bot"]}/from_clients', payload=json.dumps(message))
        return

    def on_connect(self, _client, _userdata, _flags, _rc, channel):
        """Callback function when connection to message broker is successful."""

        self.client.subscribe(
            f"bot/{self.state.token['token']['unencoded']['bot']}/{channel}")

    def on_message(self, _client, _userdata, msg):
        """Callback function when message received from message broker."""

        self.state.last_message = json.loads(msg.payload)

        # print('-' * 100)
        # print(f'{msg.topic} ({datetime.now().strftime("%Y-%m-%d %H:%M:%S")})\n')
        # print(json.dumps(json.loads(msg.payload), indent=4))

    def start_listen(self, channel="#"):
        """Establish persistent subscription to message broker channels."""

        if self.client is None:
            self.connect()

        # Wrap on_connect to pass channel argument
        self.client.on_connect = lambda client, userdata, flags, rc: self.on_connect(client, userdata, flags, rc, channel)
        self.client.on_message = self.on_message

        self.client.loop_start()

    def stop_listen(self):
        """End subscription to all message broker channels."""

        self.client.loop_stop()
        self.client.disconnect()

        return
