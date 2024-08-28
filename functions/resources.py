"""
Resources class.
"""

# └── functions/resources.py
#     ├── [BROKER] mark_point()
#     ├── [BROKER] sort_points()
#     ├── [BROKER] sequence()
#     ├── [BROKER] get_seed_tray_cell()
#     ├── [BROKER] detect_weeds()
#     ├── [BROKER] lua()
#     ├── [BROKER] if_statement()
#     └── [BROKER] assertion()

from .broker import BrokerConnect
from .information import Information

class Resources():
    """Resources class."""
    def __init__(self, state):
        self.broker = BrokerConnect(state)
        self.info = Information(state)

    def mark_coord(self, x, y, z, field, mark_as): # TODO: Fix "label" and TODO: rename mark_point()
        """Marks (x, y, z) coordinate with specified label."""

        mark_coord_message = {
            "kind": "update_resource",
            "args": {
                "resource": {
                    "kind": "identifier",
                    "args": {
                        "label": "test_location" # What is happening here??
                    }
                }
            },
            "body": [{
                "kind": "pair",
                "args": {
                    "label": field,
                    "value": mark_as
                }
            }]
        }

    # TODO: sort_points(points, method)

    def sequence(self, sequence_id):
        """Executes a predefined sequence."""

        sequence_message = {
            "kind": "execute",
            "args": {
                "sequence_id": sequence_id
            }
        }

        self.broker.publish(sequence_message)

        self.broker.state.print_status(description="Triggered sequence {sequence_id} .")

    def get_seed_tray_cell(self, tray_id, tray_cell):
        """Identifies and returns the location of specified cell in the seed tray."""

        tray_data = self.info.get_info("points", tray_id)

        cell = tray_cell.upper()

        seeder_needle_offset = 17.5
        cell_spacing = 12.5

        cells = {
            "A1": {"x": 0, "y": 0},
            "A2": {"x": 0, "y": 1},
            "A3": {"x": 0, "y": 2},
            "A4": {"x": 0, "y": 3},

            "B1": {"x": -1, "y": 0},
            "B2": {"x": -1, "y": 1},
            "B3": {"x": -1, "y": 2},
            "B4": {"x": -1, "y": 3},

            "C1": {"x": -2, "y": 0},
            "C2": {"x": -2, "y": 1},
            "C3": {"x": -2, "y": 2},
            "C4": {"x": -2, "y": 3},

            "D1": {"x": -3, "y": 0},
            "D2": {"x": -3, "y": 1},
            "D3": {"x": -3, "y": 2},
            "D4": {"x": -3, "y": 3}
        }

        if tray_data["pointer_type"] != "ToolSlot":
            raise ValueError("Seed Tray variable must be a seed tray in a slot")
        if cell not in cells:
            raise ValueError("Seed Tray Cell must be one of **A1** through **D4**")

        flip = 1
        if tray_data["pullout_direction"] == 1:
            flip = 1
        elif tray_data["pullout_direction"] == 2:
            flip = -1
        else:
            raise ValueError("Seed Tray **SLOT DIRECTION** must be `Positive X` or `Negative X`")

        a1 = {
            "x": tray_data["x"] - seeder_needle_offset + (1.5 * cell_spacing * flip),
            "y": tray_data["y"] - (1.5 * cell_spacing * flip),
            "z": tray_data["z"]
        }

        offset = {
            "x": cell_spacing * cells[cell]["x"] * flip,
            "y": cell_spacing * cells[cell]["y"] * flip
        }

        curr_x = a1["x"] + offset["x"]
        curr_y = a1["y"] + offset["y"]
        curr_z = a1["z"]

        self.broker.state.print_status(description=f"Cell {tray_cell} is at ({curr_x}, {curr_y}, {curr_z}).")
        return curr_x, curr_y, curr_z

    def detect_weeds(self):
        """Scans the garden to detect weeds."""

        detect_weeds_message = {
            "kind": "execute_script",
            "args": {
                "label": "plant-detection"
            }
        }

        self.broker.publish(detect_weeds_message)

    def lua(self, code_snippet):
        """Executes custom Lua code snippets to perform complex tasks or automations."""

        lua_message = {
            "kind": "lua",
            "args": {
                "lua": code_snippet.strip()
            }
        }

        self.broker.publish(lua_message)

        self.broker.state.print_status(description="Triggered lua code execution .")

    def if_statement(self, variable, operator, value, then_id, else_id): # TODO: add "do nothing" functionality
        """Performs conditional check and executes actions based on the outcome."""

        if_statement_message = {
            "kind": "_if",
            "args": {
                "lhs": variable,
                "op": operator,
                "rhs": value,
                "_then": {
                    "kind": "execute",
                    "args": {
                        "sequence_id": then_id
                    }
                },
                "_else": {
                    "kind": "execute",
                    "args": {
                        "sequence_id": else_id
                    }
                }
            }
        }

        self.broker.publish(if_statement_message)

        self.broker.state.print_status(description="Triggered if statement .")

    def assertion(self, code, as_type, sequence_id=""): # TODO: add "continue" functionality
        """Evaluates an expression."""

        assertion_message = {
            "kind": "assertion",
            "args": {
                "lua": code,
                "_then": {
                    "kind": "execute",
                    "args": {
                        "sequence_id": sequence_id # Recovery sequence ID
                    }
                },
                "assertion_type": as_type # If test fails, do this
            }
        }

        self.broker.publish(assertion_message)

        self.broker.state.print_status(description="Triggered assertion .")
