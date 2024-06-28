# farmbot_BROKER.py

import sys
import json

import paho.mqtt.client as mqtt

class FarmbotBroker():
    def __init__(self):
        self.token = None
        self.client = None

    def check_token(self):
        if self.token is None:
            print("ERROR: You have no token, please call `get_token` using your login credentials and the server you wish to connect to.")
            sys.exit(1)

    def connect(self):
        self.check_token()
        
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

    def publish(self, PAYLOAD):
        if self.client is None:
            self.connect()

        self.client.publish(
            f'bot/{self.token["token"]["unencoded"]["bot"]}/from_clients',
            payload=json.dumps(PAYLOAD)
        )

    def disconnect(self):
        if self.client is not None:
            self.client.loop_stop()
            self.client.disconnect()
            # Add self.client = None?