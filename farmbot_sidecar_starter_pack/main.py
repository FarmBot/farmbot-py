"""
Farmbot class.
"""

from .state import State
from .functions.api import ApiConnect
from .functions.basic_commands import BasicCommands
from .functions.broker import BrokerConnect
from .functions.camera import Camera
from .functions.information import Information
from .functions.jobs import JobHandling
from .functions.messages import MessageHandling
from .functions.movements import MovementControls
from .functions.peripherals import Peripherals
from .functions.resources import Resources
from .functions.tools import ToolControls

VERSION = "1.5.0"


class Farmbot():
    """Farmbot class."""
    __version__ = VERSION

    def __init__(self):
        self.state = State()

        # Initialize other components without the token initially
        self.api = ApiConnect(self.state)
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
        """Set output verbosity level."""
        self.state.verbosity = value

    def set_timeout(self, duration, key="listen"):
        """Set timeout value in seconds."""
        if key == "all":
            for timeout_key in self.state.timeout:
                self.state.timeout[timeout_key] = duration
        else:
            self.state.timeout[key] = duration

    def set_token(self, token):
        """Set FarmBot authorization token."""
        self.state.token = token

    # api.py

    def get_token(self, email, password, server="https://my.farm.bot"):
        """Get FarmBot authorization token. Server is 'https://my.farm.bot' by default."""
        return self.api.get_token(email, password, server)

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
        """Reboots the FarmBot OS and re-initializes the device."""
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

    def publish(self, message):
        """Publish message to the message broker."""
        return self.broker.publish(message)

    def listen(self, channel="#", duration=None):
        """Listen to a message broker channel for the provided duration in seconds."""
        return self.broker.listen(channel, duration)

    # camera.py

    def calibrate_camera(self):
        """Performs camera calibration. This action will reset camera calibration settings."""
        return self.camera.calibrate_camera()

    def take_photo(self):
        """Takes photo using the device camera and uploads it to the web app."""
        return self.camera.take_photo()

    # information.py

    def api_get(self, endpoint, database_id=None):
        """Get information about a specific endpoint."""
        return self.info.api_get(endpoint, database_id)

    def api_patch(self, endpoint, new_data, database_id=None):
        """Change information contained within an endpoint."""
        return self.info.api_patch(endpoint, new_data, database_id)

    def api_post(self, endpoint, new_data):
        """Create new information contained within an endpoint."""
        return self.info.api_post(endpoint, new_data)

    def api_delete(self, endpoint, id=None):
        """Delete information contained within an endpoint."""
        return self.info.api_delete(endpoint, id)

    def safe_z(self):
        """Returns the highest safe point along the z-axis."""
        return self.info.safe_z()

    def garden_size(self):
        """Returns size of garden bed."""
        return self.info.garden_size()

    def group(self, group_id=None):
        """Returns all group info or single by id."""
        return self.info.group(group_id)

    def curve(self, curve_id=None):
        """Returns all curve info or single by id."""
        return self.info.curve(curve_id)

    def measure_soil_height(self):
        """Use the camera to determine soil height at the current location."""
        return self.info.measure_soil_height()

    def read_status(self):
        """Returns the FarmBot status tree."""
        return self.info.read_status()

    def read_pin(self, pin_number, mode=0):
        """Reads the current value of the specified pin."""
        return self.info.read_pin(pin_number, mode)

    def read_sensor(self, sensor_name):
        """Reads the given sensor."""
        return self.info.read_sensor(sensor_name)

    # jobs.py

    def get_job(self, job_str=None):
        """Retrieves the status or details of the specified job."""
        return self.jobs.get_job(job_str)

    def set_job(self, job_str, status_message, value):
        """Initiates or modifies job with given parameters."""
        return self.jobs.set_job(job_str, status_message, value)

    def complete_job(self, job_str):
        """Marks job as completed and triggers any associated actions."""
        return self.jobs.complete_job(job_str)

    # messages.py

    def log(self, message_str, message_type="info", channel="ticker"):
        """Sends new log message via the API."""
        return self.messages.log(message_str, message_type, channel)

    def message(self, message_str, message_type="info", channel="ticker"):
        """Sends new log message via the message broker."""
        return self.messages.message(message_str, message_type, channel)

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

    def find_axis_length(self, axis="all"):
        """Finds the length of a specified axis."""
        return self.movements.find_axis_length(axis)

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

    def write_pin(self, pin_number, value, mode=0):
        """Writes a new value to the specified pin."""
        return self.peripherals.write_pin(pin_number, value, mode)

    def control_peripheral(self, peripheral_name, value, mode=None):
        """Set peripheral value and mode."""
        return self.peripherals.control_peripheral(peripheral_name, value, mode)

    def toggle_peripheral(self, peripheral_name):
        """Toggles the state of a specific peripheral between `on` and `off`."""
        return self.peripherals.toggle_peripheral(peripheral_name)

    def on(self, pin_number):
        """Turns specified pin number `on` (100%)."""
        return self.peripherals.on(pin_number)

    def off(self, pin_number):
        """Turns specified pin number `off` (0%)."""
        return self.peripherals.off(pin_number)

    # resources.py

    def sequence(self, sequence_name):
        """Executes a predefined sequence."""
        return self.resources.sequence(sequence_name)

    def get_seed_tray_cell(self, tray_name, tray_cell):
        """Identifies and returns the location of specified cell in the seed tray."""
        return self.resources.get_seed_tray_cell(tray_name, tray_cell)

    def detect_weeds(self):
        """Scans the garden to detect weeds."""
        return self.resources.detect_weeds()

    def lua(self, code_snippet):
        """Executes custom Lua code snippets to perform complex tasks or automations."""
        return self.resources.lua(code_snippet)

    def if_statement(self, variable, operator, value, then_sequence_name=None, else_sequence_name=None, named_pin_type=None):
        """Performs conditional check and executes actions based on the outcome."""
        return self.resources.if_statement(variable, operator, value, then_sequence_name, else_sequence_name, named_pin_type)

    def assertion(self, code, assertion_type, recovery_sequence_name=None):
        """Evaluates an expression."""
        return self.resources.assertion(code, assertion_type, recovery_sequence_name)

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

    def dispense(self, milliliters, tool_name, pin):
        """Dispenses user-defined amount of liquid in milliliters."""
        return self.tools.dispense(milliliters, tool_name, pin)