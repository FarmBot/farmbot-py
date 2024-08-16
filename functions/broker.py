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

    # def connect() --> connect to message broker to send messages
    # def disconnect() --> disconnect from message broker

    # def publish() --> send message via message broker

    # def on_connect() --> subscribe to messages from specific broker channel
    # def on_message() --> update message queue with latest response

    # def start_listen() --> start listening to broker channel (print each message if echo == true)
    # def stop_listen() --> stop listening to broker channel

    def connect(self):
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
        if self.client is not None:
            self.client.loop_stop()
            self.client.disconnect()

    def publish(self, message):

        if self.client is None:
            self.connect()

        self.client.publish(f'bot/{self.state.token["token"]["unencoded"]["bot"]}/from_clients', payload=json.dumps(message))

    def on_connect(self, _client, _userdata, _flags, _rc, channel):
        self.client.subscribe(
            f"bot/{self.state.token['token']['unencoded']['bot']}/{channel}")

    def on_message(self, _client, _userdata, msg):
        self.state.last_message = json.loads(msg.payload)

        # print('-' * 100)
        # # Print channel
        # print(f'{msg.topic} ({datetime.now().strftime("%Y-%m-%d %H:%M:%S")})\n')
        # # Print message
        # print(json.dumps(json.loads(msg.payload), indent=4))

    def start_listen(self, channel="#"):
        # Subscribe to all channels with "#"
        if self.client is None:
            self.connect()

        # Wrap on_connect to pass channel argument
        self.client.on_connect = lambda client, userdata, flags, rc: self.on_connect(client, userdata, flags, rc, channel)
        self.client.on_message = self.on_message

        self.client.loop_start()

    def stop_listen(self):
        self.client.loop_stop()
        self.client.disconnect()
