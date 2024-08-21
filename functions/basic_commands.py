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
        """Pauses execution for a certain number of milliseconds."""

        self.broker.state.print_status("wait()", description=f"Waiting for {duration} milliseconds...")

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
        return

    def e_stop(self):
        """Emergency locks (E-stops) the Farmduino microcontroller."""

        self.broker.state.print_status("e_stop()", description=f"Triggered device emergency stop at: {datetime.now()}")

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
        return

    def unlock(self):
        """Unlocks a locked (E-stopped) device."""

        self.broker.state.print_status("unlock()", description=f"Triggered device unlock at: {datetime.now()}")

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
        return

    def reboot(self):
        """Reboots the FarmBot OS and reinitializes the device."""

        self.broker.state.print_status("reboot()", description=f"Triggered device reboot at: {datetime.now()}")

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
        return

    def shutdown(self):
        """Shuts down the FarmBot OS and turns the device off."""

        self.broker.state.print_status("shutdown()", description=f"Triggered device shutdown at: {datetime.now()}")

        shutdown_message = {
            **RPC_REQUEST,
            "body": [{
                "kind": "power_off",
                "args": {}
            }]
        }

        self.broker.publish(shutdown_message)
        return
