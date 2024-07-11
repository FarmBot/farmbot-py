import json

from datetime import datetime
import paho.mqtt.client as mqtt

# broker_functions.py -> broker_connect.py

class BrokerConnect():
    def __init__(self):
        self.token = None
        self.client = None

    # connect() --> establish connection to message broker
    # disconnect() --> disconnect from message broker

    # publish()

    # on_connect() --> subscribe to channel
    # on_message() --> print channel/message

    # def on_connect(self, client, *_args):
    #     # subscribe to all channels
    #     self.client.subscribe(f"bot/{self.token['token']['unencoded']['bot']}/#")
    #     print('connected')

    # def status_connect(self, client, *_args):
    #     # Subscribe to specific channel
    #     device_info = self.api.get('device')
    #     device_id = device_info['id']

    #     client.subscribe("bot/device_4652/status")
    #     print('connected via status_connect()')

    def sub_all(self, client, *_args):
        """Subscribe to all message broker channels."""

        self.client.subscribe(f"bot/{self.token['token']['unencoded']['bot']}/#")
        print("Connected to all channels.")

    def sub_single(self, client, *_args, channel):
        """Subscribe to specific message broker channel."""

        self.client.subscribe("bot/{device_id}/{channel}")
        print("Connected to "+channel+".")

    def on_message(self, _client, _userdata, msg):
        print('-' * 100)
        # print channel
        print("Channel:")
        print(f'{msg.topic} ({datetime.now().strftime("%Y-%m-%d %H:%M:%S")})\n')
        # print message
        print("Message:")
        print(json.dumps(json.loads(msg.payload), indent=4))

    def connect(self):
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

        # self.client.on_connect = status_connect
        # self.client.on_message = on_message

        self.client.loop_start()

    def disconnect(self):
        if self.client is not None:
            self.client.loop_stop()
            self.client.disconnect()

    def publish(self, message):
        if self.client is None:
            self.connect()

        self.client.publish(
            f'bot/{self.token["token"]["unencoded"]["bot"]}/from_clients',
            payload=json.dumps(message)
        )
