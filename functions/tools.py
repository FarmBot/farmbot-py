"""
ToolControls class.
"""

# └── functions/tools.py
#     ├── [BROKER] verify_tool()
#     ├── [BROKER] mount_tool()
#     ├── [BROKER] dismount_tool()
#     ├── [BROKER] water()
#     └── [BROKER] dispense()

from .imports import *
from .broker import BrokerConnect
from .resources import Resources

class ToolControls():
    def __init__(self, state):
        self.broker = BrokerConnect(state)
        self.resource = Resources(state)

    # TODO: verify_tool()

    def mount_tool(self, tool_str):
        """Mounts the given tool and pulls it out of assigned slot."""

        lua_code = f"""
            mount_tool("{tool_str}")
        """

        self.resource.lua(lua_code)

        self.broker.state.print_status("mount_tool()", description=f"Mounting {tool_str} tool.")
        return

    def dismount_tool(self):
        """Dismounts the currently mounted tool into assigned slot."""

        lua_code = """
            dismount_tool()
        """

        self.resource.lua(lua_code)

        self.broker.state.print_status("mount_tool()", description="Dismounting tool.")
        return

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

        self.broker.state.print_status("mount_tool()", description=f"Watering plant {plant_id}...")
        return

    def dispense(self, mL, tool_str, pin):
        """Dispenses user-defined amount of liquid in milliliters."""

        lua_code = f"""
            dispense({mL}, {{tool_name = "{tool_str}", pin = {pin}}})
        """

        self.resource.lua(lua_code)

        self.broker.state.print_status("mount_tool()", description=f"Dispensing {mL} from tool {tool_str}...")
        return
