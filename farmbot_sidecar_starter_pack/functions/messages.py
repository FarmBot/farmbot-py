"""
MessageHandling class.
"""

# └── functions/messages.py
#     ├── [API] log()
#     ├── [BROKER] message()
#     ├── [BROKER] debug()
#     └── [BROKER] toast()

from .broker import BrokerConnect
from .api import ApiConnect
from .information import Information

MESSAGE_TYPES = ["assertion", "busy", "debug",
                 "error", "fun", "info", "success", "warn"]
CHANNELS = ["ticker", "toast", "email", "espeak"]


def validate_log_options(message_type, channel):
    """Validate the message type and channel options."""
    if message_type not in MESSAGE_TYPES:
        raise ValueError(
            f"Invalid message type: `{message_type}` not in {MESSAGE_TYPES}")
    if channel not in CHANNELS:
        raise ValueError(f"Invalid channel: {channel} not in {CHANNELS}")


class MessageHandling():
    """Message handling class."""
    def __init__(self, state):
        self.broker = BrokerConnect(state)
        self.api = ApiConnect(state)
        self.info = Information(state)
        self.state = state

    def log(self, message_str, message_type="info", channel="ticker"):
        """Sends new log message via the API."""
        self.state.print_status(description="Sending new log message to the API.")

        validate_log_options(message_type, channel)

        log_message = {
            "message": message_str,
            "type": message_type,
            "channels": [channel],
        }

        self.info.api_post("logs", log_message)

    def message(self, message_str, message_type="info", channel="ticker"):
        """Sends new log message via the message broker."""
        self.state.print_status(description="Sending new log message to the message broker.")

        validate_log_options(message_type, channel)

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

        self.broker.publish(message)

    def debug(self, message_str):
        """Sends debug message used for developer information or troubleshooting."""
        self.state.print_status(description="Sending debug message to the message broker.")

        self.message(message_str, "debug", "ticker")

    def toast(self, message_str):
        """Sends a message that pops up on the user interface briefly."""
        self.state.print_status(description="Sending toast message to the message broker.")

        self.message(message_str, "info", "toast")
