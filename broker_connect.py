import json

from datetime import datetime
import paho.mqtt.client as mqtt

class BrokerConnect():
    def __init__(self):
        self.token = None
        self.client = None

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
