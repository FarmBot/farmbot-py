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
    def __init__(self, state):
        self.broker = BrokerConnect(state)
        self.auth = Authentication(state)

    def log(self, message_str, type=None, channel=None):
        """Sends new log message via the API."""

        log_message = {
            "message": message_str,
            "type": type, # https://software.farm.bot/v15/app/intro/jobs-and-logs#log-types
            "channel": channel # Specifying channel does not do anything
        }

        endpoint = 'logs'
        id = None

        self.auth.request('POST', endpoint, id, log_message)
        return

    def message(self, message_str, type=None, channel="ticker"):
        """Sends new log message via the message broker."""

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
        return

    def debug(self, message_str):
        """Sends debug message used for developer information or troubleshooting."""

        self.message(message_str, "debug", "ticker")
        return

    def toast(self, message_str):
        """Sends a message that pops up on the user interface briefly."""

        self.message(message_str, "info", "toast")
        return
