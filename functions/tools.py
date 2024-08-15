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
    def __init__(self, token):
        self.token = token
        self.broker = BrokerConnect(token)
        self.resource = Resources(token)

    # TODO: verify_tool() --> get broker message example
        # Verify tool exists at xyz coord
        # Return xyz coord and info(?)

    def mount_tool(self, tool_str):
        # Mount tool at xyz coord
        # No inherent return value
        lua_code = f"""
            mount_tool("{tool_str}")
        """

        self.resource.lua(lua_code)

    def dismount_tool(self):
        # Dismount tool (at xyz coord?)
        # No inherent return value
        lua_code = """
            dismount_tool()
        """

        self.resource.lua(lua_code)

    def water(self, plant_id):
        # Water the given plant
        # No inherent return value
        lua_code = f"""
            plant = api({{
                method = "GET",
                url = "/api/points/{plant_id}"
            }})
            water(plant)
        """

        self.resource.lua(lua_code)

    def dispense(self, mL, tool_str, pin):
        # Dispense from source at all or single xyz coords
        # No inherent return value
        lua_code = f"""
            dispense({mL}, {{tool_name = "{tool_str}", pin = {pin}}})
        """

        self.resource.lua(lua_code)
