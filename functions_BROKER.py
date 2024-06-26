# farmbot_BROKER.py

import json

import paho.mqtt.publish as publish
import paho.mqtt.client as client

from functions_API import FarmbotAPI

API = FarmbotAPI()

class FarmbotBroker():
    def __init__(self):
        print("")

    def publish(self, PAYLOAD):
        API.check_token()

        publish.single(
            f'bot/{API.token['token']['unencoded']['bot']}/from_clients',
            payload=json.dumps(PAYLOAD),
            hostname=API.token['token']['unencoded']['mqtt'],
            auth={
                'username': API.token['token']['unencoded']['bot'],
                'password': API.token['token']['encoded']
            }
        )