"""
MessageHandling class.
"""

# └── functions/messages.py
#     ├── [API] log()
#     ├── [BROKER] message()
#     ├── [BROKER] debug()
#     └── [BROKER] toast()

from .broker import BrokerConnect
from .authentication import Authentication

class MessageHandling():
    """Message handling class."""
    def __init__(self, state):
        self.broker = BrokerConnect(state)
        self.auth = Authentication(state)

    def log(self, message_str, message_type=None, channel=None):
        """Sends new log message via the API."""

        log_message = {
            "message": message_str,
            "type": message_type, # https://software.farm.bot/v15/app/intro/jobs-and-logs#log-types
            "channel": channel # Specifying channel does not do anything
        }

        endpoint = 'logs'
        database_id = None

        self.auth.request('POST', endpoint, database_id, log_message)

        self.broker.state.print_status(description="New log message sent via API.")

    def message(self, message_str, message_type=None, channel="ticker"):
        """Sends new log message via the message broker."""

        message = {
            "kind": "send_message",
            "args": {
                "message": message_str,
                "message_type": message_type,
            },
            "body": [{
                "kind": "channel",
                "args": {
                    "channel_name": channel
                }
            }]
        }

        message = self.broker.wrap_message(message, priority=600)

        self.broker.publish(message)

        self.broker.state.print_status(description="New log message sent via message broker.")

    def debug(self, message_str):
        """Sends debug message used for developer information or troubleshooting."""

        self.message(message_str, "debug", "ticker")

        self.broker.state.print_status(description="New debug message sent via message broker.")

    def toast(self, message_str):
        """Sends a message that pops up on the user interface briefly."""

        self.message(message_str, "info", "toast")

        self.broker.state.print_status(description="New toast message sent via message broker.")
