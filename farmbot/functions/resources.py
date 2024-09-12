"""
Resources class.
"""

# └── functions/resources.py
#     ├── [BROKER] sort_points()
#     ├── [BROKER] sequence()
#     ├── [BROKER] get_seed_tray_cell()
#     ├── [BROKER] detect_weeds()
#     ├── [BROKER] lua()
#     ├── [BROKER] if_statement()
#     └── [BROKER] assertion()

from .broker import BrokerConnect
from .information import Information

ASSERTION_TYPES = ["abort", "recover", "abort_recover", "continue"]


def validate_assertion_type(assertion_type):
    """Validate assertion type."""
    if assertion_type not in ASSERTION_TYPES:
        msg = "Invalid assertion_type: "
        msg += f"{assertion_type} not in {ASSERTION_TYPES}"
        raise ValueError(msg)


OPERATORS = ["<", ">", "is", "not", "is_undefined"]
IF_STATEMENT_VARIABLE_STRINGS = [
    "x",
    "y",
    "z",
    *[f"pin{str(i)}" for i in range(70)]]
NAMED_PIN_TYPES = ["Peripheral", "Sensor"]


def validate_if_statement_args(named_pin_type, variable, operator):
    """Validate if statement arguments."""
    if operator not in OPERATORS:
        raise ValueError(f"Invalid operator: {operator} not in {OPERATORS}")
    if named_pin_type is None and variable not in IF_STATEMENT_VARIABLE_STRINGS:
        msg = "Invalid variable: "
        msg += f"{variable} not in {IF_STATEMENT_VARIABLE_STRINGS}"
        raise ValueError(msg)
    if named_pin_type is not None and named_pin_type not in NAMED_PIN_TYPES:
        msg = "Invalid named_pin_type: "
        msg += f"{named_pin_type} not in {NAMED_PIN_TYPES}"
        raise ValueError(msg)


class Resources():
    """Resources class."""

    def __init__(self, state):
        self.broker = BrokerConnect(state)
        self.info = Information(state)
        self.state = state

    # TODO: mark_as()

    # TODO: sort_points(points, method)

    def sequence(self, sequence_name):
        """Executes a predefined sequence."""
        self.state.print_status(
            description="Running {sequence_name} sequence.")

        sequence = self.info.get_resource_by_name(
            endpoint="sequences",
            resource_name=sequence_name,
            name_key="name")
        if sequence is None:
            return

        sequence_message = {
            "kind": "execute",
            "args": {
                "sequence_id": sequence["id"],
            }
        }

        self.broker.publish(sequence_message)

    def get_seed_tray_cell(self, tray_name, tray_cell):
        """Identifies and returns the location of specified cell in the seed tray."""
        self.state.print_status(
            description="Identifying seed tray cell location.")

        tray_tool = self.info.get_resource_by_name("tools", tray_name, "name")
        if tray_tool is None:
            return
        tray_data = self.info.get_resource_by_name(
            "points", tray_tool["id"], "tool_id", {"pointer_type": "ToolSlot"})
        if tray_data is None:
            self.state.print_status(
                description=f"{tray_name} must be mounted in a slot.",
                update_only=True)
            return

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

        if cell not in cells:
            msg = "Seed Tray Cell must be one of **A1** through **D4**"
            raise ValueError(msg)

        flip = 1
        if tray_data["pullout_direction"] == 1:
            flip = 1
        elif tray_data["pullout_direction"] == 2:
            flip = -1
        else:
            msg = "Seed Tray **SLOT DIRECTION** must be `Positive X` or `Negative X`"
            raise ValueError(msg)

        a1 = {
            "x": tray_data["x"] - seeder_needle_offset + (1.5 * cell_spacing * flip),
            "y": tray_data["y"] - (1.5 * cell_spacing * flip),
            "z": tray_data["z"]
        }

        offset = {
            "x": cell_spacing * cells[cell]["x"] * flip,
            "y": cell_spacing * cells[cell]["y"] * flip
        }

        cell_xyz = {
            "x": a1["x"] + offset["x"],
            "y": a1["y"] + offset["y"],
            "z": a1["z"],
        }

        self.state.print_status(
            description=f"Cell {tray_cell} is at {cell_xyz}.",
            update_only=True)
        return cell_xyz

    def detect_weeds(self):
        """Scans the garden to detect weeds."""
        self.state.print_status(description="Detecting weeds...")

        detect_weeds_message = {
            "kind": "execute_script",
            "args": {
                "label": "plant-detection"
            }
        }

        self.broker.publish(detect_weeds_message)

    def lua(self, lua_code):
        """Executes custom Lua code snippets to perform complex tasks or automations."""
        self.state.print_status(description="Running Lua code")

        lua_message = {
            "kind": "lua",
            "args": {
                "lua": lua_code.strip()
            }
        }

        self.broker.publish(lua_message)

    def if_statement(self,
                     variable,
                     operator,
                     value,
                     then_sequence_name=None,
                     else_sequence_name=None,
                     named_pin_type=None):
        """Performs conditional check and executes actions based on the outcome."""

        self.state.print_status(description="Executing if statement.")

        validate_if_statement_args(named_pin_type, variable, operator)
        if named_pin_type is not None:
            endpoint = named_pin_type.lower() + "s"
            resource = self.info.get_resource_by_name(endpoint, variable)
            if resource is None:
                return
            variable = {
                "kind": "named_pin",
                "args": {
                    "pin_type": named_pin_type,
                    "pin_id": resource["id"]
                }
            }

        if_statement_message = {
            "kind": "_if",
            "args": {
                "lhs": variable,
                "op": operator,
                "rhs": value,
                "_then": {"kind": "nothing", "args": {}},
                "_else": {"kind": "nothing", "args": {}},
            }
        }

        sequence_names = {
            "_then": then_sequence_name,
            "_else": else_sequence_name,
        }
        for key, sequence_name in sequence_names.items():
            if sequence_name is not None:
                sequence = self.info.get_resource_by_name(
                    endpoint="sequences",
                    resource_name=sequence_name,
                    name_key="name")
                if sequence is None:
                    return
                sequence_id = sequence["id"]
                if_statement_message["args"][key] = {
                    "kind": "execute",
                    "args": {"sequence_id": sequence_id},
                }

        self.broker.publish(if_statement_message)

    def assertion(self, lua_code, assertion_type, recovery_sequence_name=None):
        """Evaluates an expression."""
        self.state.print_status(description="Executing assertion.")

        validate_assertion_type(assertion_type)

        assertion_message = {
            "kind": "assertion",
            "args": {
                "assertion_type": assertion_type,
                "lua": lua_code,
                "_then": {"kind": "nothing", "args": {}},
            }
        }

        if recovery_sequence_name is not None:
            sequence = self.info.get_resource_by_name(
                endpoint="sequences",
                resource_name=recovery_sequence_name,
                name_key="name")
            if sequence is None:
                return
            recovery_sequence_id = sequence["id"]
            assertion_message["args"]["_then"] = {
                "kind": "execute",
                "args": {"sequence_id": recovery_sequence_id},
            }

        self.broker.publish(assertion_message)
