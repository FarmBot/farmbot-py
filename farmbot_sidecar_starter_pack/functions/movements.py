"""
MovementControls class.
"""

# └── functions/movements.py
#     ├── [BROKER] get_xyz()
#     ├── [BROKER] move()
#     ├── [BROKER] set_home()
#     ├── [BROKER] find_home()
#     ├── [BROKER] find_axis_length()
#     └── [BROKER] check_position()

from .broker import BrokerConnect
from .information import Information

AXES = ["x", "y", "z", "all"]


def validate_axis(axis):
    """Validate axis."""
    if axis not in AXES:
        raise ValueError(f"Invalid axis: {axis} not in {AXES}")


class MovementControls():
    """MovementControls class."""

    def __init__(self, state):
        self.broker = BrokerConnect(state)
        self.info = Information(state)
        self.state = state

    def move(self, x=None, y=None, z=None, safe_z=None, speed=None):
        """Moves to the specified (x, y, z) coordinate."""
        self.state.print_status(description=f"Moving to ({x}, {y}, {z}).")

        def axis_overwrite(axis, value):
            return {
                "kind": "axis_overwrite",
                "args": {
                    "axis": axis,
                    "axis_operand": {
                        "kind": "numeric",
                        "args": {
                            "number": value
                        }
                    }
                }
            }

        def safe_z_body_item():
            return {
                "kind": "safe_z",
                "args": {},
            }

        def speed_overwrite(axis, speed):
            return {
                "kind": "speed_overwrite",
                "args": {
                    "axis": axis,
                    "speed_setting": {
                        "kind": "numeric",
                        "args": {
                            "number": speed,
                        }
                    }
                }
            }

        move_message = {
            "kind": "move",
            "args": {},
            "body": [],
        }

        if x is not None:
            move_message["body"].append(axis_overwrite("x", x))

        if y is not None:
            move_message["body"].append(axis_overwrite("y", y))

        if z is not None:
            move_message["body"].append(axis_overwrite("z", z))

        if speed is not None:
            move_message["body"].append(speed_overwrite("x", speed))
            move_message["body"].append(speed_overwrite("y", speed))
            move_message["body"].append(speed_overwrite("z", speed))

        if safe_z is not None:
            move_message["body"].append(safe_z_body_item())

        self.broker.publish(move_message)

    def set_home(self, axis="all"):
        """Sets the current position as the home position for a specific axis."""
        self.state.print_status(description="Setting home position")

        validate_axis(axis)

        set_home_message = {
            "kind": "zero",
            "args": {
                "axis": axis
            }
        }
        self.broker.publish(set_home_message)

    def find_home(self, axis="all", speed=100):
        """Moves the device to the home position for a specified axis."""
        self.state.print_status(description="Finding home position")

        validate_axis(axis)

        if speed > 100 or speed < 1:
            error = "ERROR: Speed constrained to 1-100."
            self.state.print_status(description=error, update_only=True)
            self.state.error = error
            return

        message = {
            "kind": "find_home",
            "args": {
                "axis": axis,
                "speed": speed
            }
        }
        self.broker.publish(message)

    def find_axis_length(self, axis="all"):
        """Finds the length of a specified axis."""
        self.state.print_status(description="Finding axis length")

        validate_axis(axis)

        find_axis_length_message = {
            "kind": "calibrate",
            "args": {
                "axis": axis
            }
        }

        self.broker.publish(find_axis_length_message)

    def get_xyz(self):
        """Returns the current (x, y, z) coordinates of the FarmBot."""
        self.state.print_status(description="Getting current coordinates")

        tree_data = self.info.read_status()
        if tree_data is None:
            error = "ERROR: No location data available."
            self.state.print_status(description=error, update_only=True)
            self.state.error = error
            return None
        position = tree_data["location_data"]["position"]

        self.state.print_status(
            description=f"Current position: {position}.",
            update_only=True)
        return position

    def check_position(self, coordinate, tolerance):
        """Verifies position of the FarmBot within specified tolerance range."""

        self.state.print_status(
            description=f"Checking if position is {coordinate} with tolerance: {tolerance}.")

        actual_vals = self.get_xyz()

        if actual_vals is None:
            return False

        for axis in ['x', 'y', 'z']:
            user_value = coordinate[axis]
            actual_value = actual_vals[axis]
            if not actual_value - tolerance <= user_value <= actual_value + tolerance:
                description = "Farmbot is NOT at position."
                description += f"\n Current position: {actual_vals}."
                self.state.print_status(
                    description=description,
                    update_only=True)
                return False

        self.state.print_status(
            description=f"Farmbot is at position: {actual_vals}.",
            update_only=True)
        return True
