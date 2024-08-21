"""
Peripherals class.
"""

# └── functions/peripherals.py
#     ├── [BROKER] control_servo()
#     ├── [BROKER] control_peripheral()
#     ├── [BROKER] toggle_peripheral()
#     ├── [BROKER] on()
#     └── [BROKER] off()

from .imports import *
from .broker import BrokerConnect
from .information import Information

class Peripherals():
    def __init__(self, state):
        self.broker = BrokerConnect(state)
        self.info = Information(state)

    def control_servo(self, pin, angle):
        """Set servo angle between 0-100 degrees."""

        if angle < 0 or angle > 180:
            return print("ERROR: Servo angle constrained to 0-180 degrees.")
        else:
            control_servo_message = {
                **RPC_REQUEST,
                "body": [{
                    "kind": "set_servo_angle",
                    "args": {
                        "pin_number": pin,
                        "pin_value": angle # From 0 to 180
                    }
                }]
            }

        self.broker.publish(control_servo_message)
        return

    def control_peripheral(self, id, value, mode=None):
        """Set peripheral value and mode."""

        if mode is None:
            peripheral_str = self.info.get_info("peripherals", id)
            mode = peripheral_str["mode"]

        control_peripheral_message = {
            **RPC_REQUEST,
            "body": [{
                "kind": "write_pin",
                "args": {
                    "pin_value": value, # Controls ON/OFF or slider value from 0-255
                    "pin_mode": mode, # Controls digital (0) or analog (1) mode
                    "pin_number": {
                        "kind": "named_pin",
                        "args": {
                            "pin_type": "Peripheral",
                            "pin_id": id
                        }
                    }
                }
            }]
        }

        self.broker.publish(control_peripheral_message)
        return

    def toggle_peripheral(self, id):
        """Toggles the state of a specific peripheral between `on` and `off`."""

        toggle_peripheral_message = {
            **RPC_REQUEST,
            "body": [{
                "kind": "toggle_pin",
                "args": {
                    "pin_number": {
                        "kind": "named_pin",
                        "args": {
                            "pin_type": "Peripheral",
                            "pin_id": id
                        }
                    }
                }
            }]
        }

        self.broker.publish(toggle_peripheral_message)
        return # TODO: return status

    def on(self, id):
        """Turns specified peripheral `on` (100%)."""

        peripheral_str = self.info.get_info("peripherals", id)
        mode = peripheral_str["mode"]

        if mode == 1:
            self.control_peripheral(id, 255)
        elif mode == 0:
            self.control_peripheral(id, 1)

        return # TODO: return status

    def off(self, id):
        """Turns specified peripheral `off` (0%)."""

        self.control_peripheral(id, 0)

        return # TODO: return status
