"""
BasicCommands class.
"""

# └── functions/basic_commands.py
#     ├── [BROKER] wait()
#     ├── [BROKER] e_stop()
#     ├── [BROKER] unlock()
#     ├── [BROKER] reboot()
#     └── [BROKER] shutdown()

from .imports import *
from .broker import BrokerConnect


class BasicCommands():
    def __init__(self, state):
        self.broker = BrokerConnect(state)

    def wait(self, duration):
        # Tell bot to wait for some time
        wait_message = {
            "kind": "rpc_request",
            "args": {
                "label": "",
                "priority": 600
            },
            "body": [{
                "kind": "wait",
                "args": {
                    "milliseconds": duration
                }
            }]
        }
        self.broker.publish(wait_message)

        # No inherent return value
        return print("Waiting for "+str(duration)+" milliseconds...")

    def e_stop(self):
        # Tell bot to emergency stop
        stop_message = {
            "kind": "rpc_request",
            "args": {
                "label": "",
                "priority": 9000
            },
            "body": [{
                "kind": "emergency_lock",
                "args": {}
            }]
        }
        self.broker.publish(stop_message)

        # No inherent return value
        return print("Triggered device emergency stop.")

    def unlock(self):
        # Tell bot to unlock
        unlock_message = {
            "kind": "rpc_request",
            "args": {
                "label": "",
                "priority": 9000
            },
            "body": [{
                "kind": "emergency_unlock",
                "args": {}
            }]
        }
        self.broker.publish(unlock_message)

        # No inherent return value
        return print("Triggered device unlock.")

    def reboot(self):
        # Tell bot to reboot
        # No inherent return value
        reboot_message = {
            **RPC_REQUEST,
            "body": [{
                "kind": "reboot",
                "args": {
                    "package": "farmbot_os"
                }
            }]
        }

        self.broker.publish(reboot_message)
        return print("Triggered device reboot.")

    def shutdown(self):
        # Tell bot to shutdown
        # No inherent return value
        shutdown_message = {
            **RPC_REQUEST,
            "body": [{
                "kind": "power_off",
                "args": {}
            }]
        }

        self.broker.publish(shutdown_message)
        return print("Triggered device shutdown.")
