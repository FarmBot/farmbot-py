"""
Farmbot class.
"""

from imports import *

class State():
    def __init__(self):
        self.token = None
        self.error = None
        self.last_message = None
        self.verbosity = 2

    def print_status(self, function, endpoint_json=None, description=None):
        """Handle changes to output based on user-defined verbosity."""

        if self.verbosity >= 1:
            print(f"`{function}` called")
        if self.verbosity >= 2 and description:
            print(description)
        if self.verbosity >= 2 and endpoint_json:
            print(json.dumps(endpoint_json, indent=4))

class Farmbot():
    def __init__(self):
        self.state = State()

        # Initialize other components without the token initially
        self.auth = Authentication(self.state)
        self.basic = BasicCommands(self.state)
        self.broker = BrokerConnect(self.state)
        self.camera = Camera(self.state)
        self.info = Information(self.state)
        self.jobs = JobHandling(self.state)
        self.messages = MessageHandling(self.state)
        self.movements = MovementControls(self.state)
        self.peripherals = Peripherals(self.state)
        self.resources = Resources(self.state)
        self.tools = ToolControls(self.state)

    def set_verbosity(self, value):
        if value <= -1 or value >= 3:
            return print("ERROR: verbosity must be between 0-2")

        self.state.verbosity = value

    # authentication.py

    def get_token(self, email, password, server="https://my.farm.bot"):
        """Get FarmBot authorization token. Server is 'https://my.farm.bot' by default."""
        return self.auth.get_token(email, password, server)

    # basic_commands.py

    def wait(self, duration):
        """Pauses execution for a certain number of milliseconds."""
        return self.basic.wait(duration)

    def e_stop(self):
        """Emergency locks (E-stops) the Farmduino microcontroller."""
        return self.basic.e_stop()

    def unlock(self):
        """Unlocks a locked (E-stopped) device."""
        return self.basic.unlock()

    def reboot(self):
        """Reboots the FarmBot OS and reinitializes the device."""
        return self.basic.reboot()

    def shutdown(self):
        """Shuts down the FarmBot OS and turns the device off."""
        return self.basic.shutdown()

    # broker.py

    def connect_broker(self):
        """Establish persistent connection to send messages via message broker."""
        return self.broker.connect()

    def disconnect_broker(self):
        """Disconnect from the message broker."""
        return self.broker.disconnect()

    def start_listen(self, channel="#"):
        """Establish persistent subscription to message broker channels."""
        return self.broker.start_listen(channel)

    def stop_listen(self):
        """End subscription to all message broker channels."""
        return self.broker.stop_listen()

    # camera.py

    def calibrate_camera(self):
        """Performs camera calibration. This action will reset camera calibration settings."""
        return self.camera.calibrate_camera()

    def take_photo(self):
        """Takes photo using the device camera and uploads it to the web app."""
        return self.camera.take_photo()

    # information.py

    def get_info(self, endpoint, id=None):
        """Get information about a specific endpoint."""
        return self.info.get_info(endpoint, id)

    def edit_info(self, endpoint, new_data, id=None):
        """Change information contained within an endpoint."""
        return self.info.edit_info(endpoint, new_data, id)

    def add_info(self, endpoint, new_data):
        """Create new informated contained within an endpoint."""
        return self.info.add_info(endpoint, new_data)

    def safe_z(self):
        """Returns the highest safe point along the z-axis."""
        return self.info.safe_z()

    def garden_size(self):
        """Returns x-axis length, y-axis length, and area of garden bed."""
        return self.info.garden_size()

    def group(self, id=None):
        """Returns all group info or single by id."""
        return self.info.group(id)

    def curve(self, id=None):
        """Returns all curve info or single by id."""
        return self.info.curve(id)

    def soil_height(self):
        """Use the camera to determine soil height at the current location."""
        return self.info.soil_height()

    def read_status(self):
        """Returns the FarmBot status tree."""
        return self.info.read_status()

    def read_sensor(self, id):
        """Reads the given pin by id."""
        return self.info.read_sensor(id)

    # jobs.py

    def get_job(self, job_str):
        """Retrieves the status or details of the specified job."""
        return self.jobs.get_job(job_str)

    def set_job(self, job_str, status_message, value):
        """Initiates or modifies job with given parameters."""
        return self.jobs.set_job(job_str, status_message, value)

    def complete_job(self, job_str):
        """Marks job as completed and triggers any associated actions."""
        return self.jobs.complete_job(job_str)

    # messages.py

    def log(self, message_str, type=None, channel=None):
        """Sends new log message via the API."""
        return self.messages.log(message_str, type, channel)

    def message(self, message_str, type=None, channel="ticker"):
        """Sends new log message via the message broker."""
        return self.messages.message(message_str, type, channel)

    def debug(self, message_str):
        """Sends debug message used for developer information or troubleshooting."""
        return self.messages.debug(message_str)

    def toast(self, message_str):
        """Sends a message that pops up on the user interface briefly."""
        return self.messages.toast(message_str)

    # movements.py

    def move(self, x, y, z):
        """Moves to the specified (x, y, z) coordinate."""
        return self.movements.move(x, y, z)

    def set_home(self, axis="all"):
        """Sets the current position as the home position for a specific axis."""
        return self.movements.set_home(axis)

    def find_home(self, axis="all", speed=100):
        """Moves the device to the home position for a specified axis."""
        return self.movements.find_home(axis, speed)

    def axis_length(self, axis="all"):
        """Returns the length of a specified axis."""
        return self.movements.axis_length(axis)

    def get_xyz(self):
        """Returns the current (x, y, z) coordinates of the FarmBot."""
        return self.movements.get_xyz()

    def check_position(self, user_x, user_y, user_z, tolerance):
        """Verifies position of the FarmBot within specified tolerance range."""
        return self.movements.check_position(user_x, user_y, user_z, tolerance)

    # peripherals.py

    def control_servo(self, pin, angle):
        """Set servo angle between 0-100 degrees."""
        return self.peripherals.control_servo(pin, angle)

    def control_peripheral(self, id, value, mode=None):
        """Set peripheral value and mode."""
        return self.peripherals.control_peripheral(id, value, mode)

    def toggle_peripheral(self, id):
        """Toggles the state of a specific peripheral between `on` and `off`."""
        return self.peripherals.toggle_peripheral(id)

    def on(self, id):
        """Turns specified peripheral `on` (100%)."""
        return self.peripherals.on(id)

    def off(self, id):
        """Turns specified peripheral `off` (0%)."""
        return self.peripherals.off(id)

    # resources.py

    def mark_coord(self, x, y, z, property, mark_as):
        """Marks (x, y, z) coordinate with specified label."""
        return self.resources.mark_coord(x, y, z, property, mark_as)

    def sequence(self, sequence_id):
        """Executes a predefined sequence."""
        return self.resources.sequence(sequence_id)

    def get_seed_tray_cell(self, tray_id, tray_cell):
        """Identifies and returns the location of specified cell in the seed tray."""
        return self.resources.get_seed_tray_cell(tray_id, tray_cell)

    def detect_weeds(self):
        """Scans the garden to detect weeds."""
        return self.resources.detect_weeds()

    def lua(self, code_snippet):
        """Executes custom Lua code snippets to perform complex tasks or automations."""
        return self.resources.lua(code_snippet)

    def if_statement(self, variable, operator, value, then_id, else_id):
        """Performs conditional check and executes actions based on the outcome."""
        return self.resources.if_statement(variable, operator, value, then_id, else_id)

    def assertion(self, code, as_type, id=""):
        """Evaluates an expression."""
        return self.resources.assertion(code, as_type, id)

    # tools.py

    def mount_tool(self, tool_str):
        """Mounts the given tool and pulls it out of assigned slot."""
        return self.tools.mount_tool(tool_str)

    def dismount_tool(self):
        """Dismounts the currently mounted tool into assigned slot."""
        return self.tools.dismount_tool()

    def water(self, plant_id):
        """Moves to and waters plant based on age and assigned watering curve."""
        return self.tools.water(plant_id)

    def dispense(self, mL, tool_str, pin):
        """Dispenses user-defined amount of liquid in milliliters."""
        return self.tools.dispense(mL, tool_str, pin)
