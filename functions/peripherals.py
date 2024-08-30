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
        self.state.print_status(description=f"Setting servo angle to {angle}.")

        if angle < 0 or angle > 180:
            error = "ERROR: Servo angle constrained to 0-180 degrees."
            self.state.print_status(description=error, update_only=True)
            self.state.error = error
            return

        control_servo_message = {
            "kind": "set_servo_angle",
            "args": {
                "pin_number": pin,
                "pin_value": angle # From 0 to 180
            }
        }

        self.broker.publish(control_servo_message)

        return

    def control_peripheral(self, peripheral_name, value, mode=None):
        """Set peripheral value and mode."""
        self.state.print_status(description=f"Setting {peripheral_name} to {value}.")

        peripheral = self.info.get_resource_by_name("peripherals", peripheral_name)
        if peripheral is None:
            return
        peripheral_id = peripheral["id"]
        pin_mode = peripheral["mode"] if mode is None else mode

        control_peripheral_message = {
            "kind": "write_pin",
            "args": {
                "pin_value": value, # Controls ON/OFF or slider value from 0-255
                "pin_mode": pin_mode, # Controls digital (0) or analog (1) mode
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

    def toggle_peripheral(self, peripheral_name):
        """Toggles the state of a specific peripheral between `on` and `off`."""
        self.state.print_status(description=f"Toggling {peripheral_name}.")
        peripheral = self.info.get_resource_by_name("peripherals", peripheral_name)
        if peripheral is None:
            return
        peripheral_id = peripheral["id"]
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

    def on(self, pin_number):
        """Turns specified pin number `on` (100%)."""
        self.state.print_status(description=f"Turning ON pin number {pin_number}.")

        on_message = {
            "kind": "write_pin",
            "args": {
                "pin_value": 1,
                "pin_mode": 0,
                "pin_number": pin_number,
            }
        }

        self.broker.publish(on_message)

    def off(self, pin_number):
        """Turns specified pin number `off` (0%)."""
        self.state.print_status(description=f"Turning OFF pin number {pin_number}.")

        off_message = {
            "kind": "write_pin",
            "args": {
                "pin_value": 0,
                "pin_mode": 0,
                "pin_number": pin_number,
            }
        }

        self.broker.publish(off_message)
