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
        verbosity_level = {
            1: lambda: print("`wait` called"),
            2: lambda: print(f"Waiting for {duration} milliseconds...")
        }

        verbosity_level[self.broker.state.verbosity]()

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

    def e_stop(self):
        verbosity_level = {
            1: lambda: print("`e_stop` called"),
            2: lambda: print(f"Triggered device emergency stop at: {datetime.now()}")
        }

        verbosity_level[self.broker.state.verbosity]()

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

    def unlock(self):
        verbosity_level = {
            1: lambda: print("`unlock` called"),
            2: lambda: print(f"Triggered device unlock at: {datetime.now()}")
        }

        verbosity_level[self.broker.state.verbosity]()

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

    def reboot(self):
        verbosity_level = {
            1: lambda: print("`reboot` called"),
            2: lambda: print(f"Triggered device reboot at: {datetime.now()}")
        }

        verbosity_level[self.broker.state.verbosity]()

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

    def shutdown(self):
        verbosity_level = {
            1: lambda: print("`shutdown` called"),
            2: lambda: print(f"Triggered device shutdown at: {datetime.now()}")
        }

        verbosity_level[self.broker.state.verbosity]()

        shutdown_message = {
            **RPC_REQUEST,
            "body": [{
                "kind": "power_off",
                "args": {}
            }]
        }

        self.broker.publish(shutdown_message)
