"""
MessageHandling class.
"""

# └── functions/messages.py
#     ├── [API] log()
#     ├── [BROKER] message()
#     ├── [BROKER] debug()
#     └── [BROKER] toast()

from .imports import *
from .broker import BrokerConnect
from .authentication import Authentication

class MessageHandling():
    def __init__(self):
        self.token = None

        self.broker = BrokerConnect()
        self.auth = Authentication()

    def log(self, message_str, type=None, channel=None):
        # Send new log message via API
        log_message = {
            "message": message_str,
            "type": type, # https://software.farm.bot/v15/app/intro/jobs-and-logs#log-types
            "channel": channel # Specifying channel does not do anything
        }

        endpoint = 'logs'
        id = None

        self.auth.request('POST', endpoint, id, log_message)
        # No inherent return value

    def message(self, message_str, type=None, channel="ticker"):
        message = {
            "kind": "rpc_request",
            "args": {
                "label": "",
                "priority": 600
            },
            "body": [{
                "kind": "send_message",
                "args": {
                    "message": message_str,
                    "message_type": type
                },
                "body": [{
                    "kind": "channel",
                    "args": {
                        "channel_name": channel
                    }
                }]
            }]
        }

        self.broker.publish(message)
        # No inherent return value

    def debug(self, message_str):
        # Send "debug" type message
        self.message(message_str, "debug", "ticker")
        # No inherent return value

    def toast(self, message_str):
        # Send "toast" type message
        self.message(message_str, "info", "toast")
        # No inherent return value
