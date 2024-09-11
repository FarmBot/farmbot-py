"""
ToolControls class.
"""

# └── functions/tools.py
#     ├── [BROKER] verify_tool()
#     ├── [BROKER] mount_tool()
#     ├── [BROKER] dismount_tool()
#     ├── [BROKER] water()
#     └── [BROKER] dispense()

from .broker import BrokerConnect
from .resources import Resources


class ToolControls():
    """Tool controls class."""

    def __init__(self, state):
        self.broker = BrokerConnect(state)
        self.resource = Resources(state)
        self.state = state

    # TODO: verify_tool()

    def mount_tool(self, tool_name):
        """Mounts the given tool and pulls it out of assigned slot."""
        self.state.print_status(description=f"Mounting {tool_name} tool.")

        lua_code = f"mount_tool(\"{tool_name}\")"

        self.resource.lua(lua_code)

    def dismount_tool(self):
        """Dismounts the currently mounted tool into assigned slot."""
        self.state.print_status(description="Dismounting tool.")

        lua_code = "dismount_tool()"

        self.resource.lua(lua_code)

    @staticmethod
    def water_and_dispense_end_string(tool_name=None, pin=None):
        """Prepares water or dispense end string."""
        string = ""
        if tool_name is not None:
            string += ", {"
            string += f"tool_name = \"{tool_name}\""
        if pin is not None:
            string += ", "
            if tool_name is None:
                string += "{"
            string += f"pin = {pin}"
        if tool_name is not None or pin is not None:
            string += "})"
        else:
            string += ")"
        return string

    def water(self, plant_id, tool_name=None, pin=None):
        """Moves to and waters plant based on age and assigned watering curve."""
        self.state.print_status(description=f"Watering plant {plant_id}...")

        lua_code = f"""
            plant = api({{
                method = "GET",
                url = "/api/points/{plant_id}"
            }})
            water(plant
        """
        lua_code = lua_code.strip()
        lua_code += self.water_and_dispense_end_string(tool_name, pin)

        self.resource.lua(lua_code)

    def dispense(self, milliliters, tool_name=None, pin=None):
        """Dispenses user-defined amount of liquid in milliliters."""
        self.state.print_status(
            description=f"Dispensing {milliliters} from tool {tool_name}...")

        lua_code = f"dispense({milliliters}"
        lua_code += self.water_and_dispense_end_string(tool_name, pin)

        self.resource.lua(lua_code)
