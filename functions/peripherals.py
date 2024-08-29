"""
Peripherals class.
"""

# └── functions/peripherals.py
#     ├── [BROKER] control_servo()
#     ├── [BROKER] control_peripheral()
#     ├── [BROKER] toggle_peripheral()
#     ├── [BROKER] on()
#     └── [BROKER] off()

from .broker import BrokerConnect
from .information import Information

class Peripherals():
    """Peripherals class."""
    def __init__(self, state):
        self.broker = BrokerConnect(state)
        self.info = Information(state)
        self.state = state

    def control_servo(self, pin, angle):
        """Set servo angle between 0-100 degrees."""

        if angle < 0 or angle > 180:
            return print("ERROR: Servo angle constrained to 0-180 degrees.")

        control_servo_message = {
            "kind": "set_servo_angle",
            "args": {
                "pin_number": pin,
                "pin_value": angle # From 0 to 180
            }
        }

        self.broker.publish(control_servo_message)

        self.state.print_status(description=f"Set servo angle to {angle}.")
        return

    def control_peripheral(self, peripheral_id, value, mode=None):
        """Set peripheral value and mode."""

        if mode is None:
            peripheral_str = self.info.api_get("peripherals", peripheral_id)
            mode = peripheral_str["mode"]

        control_peripheral_message = {
            "kind": "write_pin",
            "args": {
                "pin_value": value, # Controls ON/OFF or slider value from 0-255
                "pin_mode": mode, # Controls digital (0) or analog (1) mode
                "pin_number": {
                    "kind": "named_pin",
                    "args": {
                        "pin_type": "Peripheral",
                        "pin_id": peripheral_id,
                    }
                }
            }
        }

        self.broker.publish(control_peripheral_message)

        self.state.print_status(description=f"Set peripheral {peripheral_id} to {value} with mode={mode}.")

    def toggle_peripheral(self, peripheral_id):
        """Toggles the state of a specific peripheral between `on` and `off`."""

        toggle_peripheral_message = {
            "kind": "toggle_pin",
            "args": {
                "pin_number": {
                    "kind": "named_pin",
                    "args": {
                        "pin_type": "Peripheral",
                        "pin_id": peripheral_id,
                    }
                }
            }
        }

        self.broker.publish(toggle_peripheral_message)

        self.state.print_status(description=f"Triggered toggle peripheral {peripheral_id}.")

    def on(self, peripheral_id):
        """Turns specified peripheral `on` (100%)."""

        peripheral_str = self.info.api_get("peripherals", peripheral_id)
        mode = peripheral_str["mode"]

        if mode == 1:
            self.control_peripheral(peripheral_id, 255)
        elif mode == 0:
            self.control_peripheral(peripheral_id, 1)

        self.state.print_status(description=f"Turned ON peripheral {peripheral_id}.")
        return

    def off(self, peripheral_id):
        """Turns specified peripheral `off` (0%)."""

        self.control_peripheral(peripheral_id, 0)

        self.state.print_status(description=f"Turned OFF peripheral {peripheral_id}.")
        return
