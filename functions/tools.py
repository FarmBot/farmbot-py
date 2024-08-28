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

    def mount_tool(self, tool_str):
        """Mounts the given tool and pulls it out of assigned slot."""

        lua_code = f"""
            mount_tool("{tool_str}")
        """

        self.resource.lua(lua_code)

        self.state.print_status(description=f"Mounting {tool_str} tool.")

    def dismount_tool(self):
        """Dismounts the currently mounted tool into assigned slot."""

        lua_code = """
            dismount_tool()
        """

        self.resource.lua(lua_code)

        self.state.print_status(description="Dismounting tool.")

    def water(self, plant_id):
        """Moves to and waters plant based on age and assigned watering curve."""

        lua_code = f"""
            plant = api({{
                method = "GET",
                url = "/api/points/{plant_id}"
            }})
            water(plant)
        """

        self.resource.lua(lua_code)

        self.state.print_status(description=f"Watering plant {plant_id}...")

    def dispense(self, milliliters, tool_str, pin):
        """Dispenses user-defined amount of liquid in milliliters."""

        lua_code = f"""
            dispense({milliliters}, {{tool_name = "{tool_str}", pin = {pin}}})
        """

        self.resource.lua(lua_code)

        self.state.print_status(description=f"Dispensing {milliliters} from tool {tool_str}...")
