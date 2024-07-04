# farmbot_BROKER.py

import sys
import json

import paho.mqtt.client as mqtt

from farmbot_api import FarmbotAPI

class FarmbotBroker():
    def __init__(self):
        self.api = FarmbotAPI()

        self.token = None
        self.client = None

    # BROKER
    # ├── connect()
    # ├── disconnect()
    # │
    # └── publish()

    def connect(self):
        self.api.check_token()

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
