"""
Farmbot class.
"""

from imports import *

class Farmbot():
    def __init__(self):
        self.token = None
        self.error = None

        self.echo = True

        # Initialize other components without the token initially
        self.auth = Authentication(self.token)
        self.basic = BasicCommands(self.token)
        self.broker = BrokerConnect(self.token)
        self.camera = Camera(self.token)
        self.info = Information(self.token)
        self.jobs = JobHandling(self.token)
        self.messages = MessageHandling(self.token)
        self.movements = MovementControls(self.token)
        self.peripherals = Peripherals(self.token)
        self.resources = Resources(self.token)
        self.tools = ToolControls(self.token)

    # authentication.py

    def set_token(self, token):
        self.token = token

        # Set API token (redundant--used for tests)
        self.auth.token = token

        # Propagate token to all components
        self.basic.token = token
        self.broker.token = token
        self.camera.token = token
        self.info.token = token
        self.jobs.token = token
        self.messages.token = token
        self.movements.token = token
        self.peripherals.token = token
        self.resources.token = token
        self.tools.token = token

        # Also set token for nested instances
        self.basic.broker.token = token
        self.camera.broker.token = token
        self.info.broker.token = token
        self.info.auth.token = token
        self.jobs.broker.token = token
        self.jobs.info.token = token
        self.jobs.resource.token = token
        self.messages.broker.token = token
        self.messages.auth.token = token
        self.movements.broker.token = token
        self.movements.info.token = token
        self.peripherals.broker.token = token
        self.peripherals.info.token = token
        self.resources.broker.token = token
        self.resources.info.token = token
        self.tools.broker.token = token
        self.tools.resource.token = token

    def get_token(self, email, password, server="https://my.farm.bot"):
        # Call get_token() source
        # Set authentication token for all modules

        token_data = self.auth.get_token(email, password, server)

        self.set_token(self.auth.token)
        self.error = self.auth.error

        return token_data

    # basic_commands.py

    def wait(self, duration):
        return self.basic.wait(duration)

    def e_stop(self):
        return self.basic.e_stop()

    def unlock(self):
        return self.basic.unlock()

    def reboot(self):
        return self.basic.reboot()

    def shutdown(self):
        return self.basic.shutdown()

    # broker.py

    def connect_broker(self):
        return self.broker.connect()

    def disconnect_broker(self):
        return self.broker.disconnect()

    # camera.py

    def calibrate_camera(self):
        return self.camera.calibrate_camera()

    def take_photo(self):
        return self.camera.take_photo()

    # information.py

    def get_info(self, endpoint, id=None):
        return self.info.get_info(endpoint, id)

    def set_info(self, endpoint, field, value, id=None):
        return self.info.set_info(endpoint, field, value, id)

    def safe_z(self):
        return self.info.safe_z()

    def garden_size(self):
        return self.info.garden_size()

    def group(self, id=None):
        return self.info.group(id)

    def curve(self, id=None):
        return self.info.curve(id)

    def soil_height(self):
        return self.info.soil_height()

    def read_status(self):
        return self.info.read_status()

    def read_sensor(self, id):
        return self.info.read_sensor(id)

    # jobs.py

    def get_job(self, job_str):
        return self.jobs.get_job(job_str)

    def set_job(self, job_str, status_message, value):
        return self.jobs.set_job(job_str, status_message, value)

    def complete_job(self, job_str):
        return self.jobs.complete_job(job_str)

    # messages.py

    def log(self, message_str, type=None, channel=None):
        return self.messages.log(message_str, type, channel)

    def message(self, message_str, type=None, channel="ticker"):
        return self.messages.message(message_str, type, channel)

    def debug(self, message_str):
        return self.messages.debug(message_str)

    def toast(self, message_str):
        return self.messages.toast(message_str)

    # movements.py

    def move(self, x, y, z):
        return self.movements.move(x, y, z)

    def set_home(self, axis="all"):
        return self.movements.set_home(axis)

    def find_home(self, axis="all", speed=100):
        return self.movements.find_home(axis, speed)

    def axis_length(self, axis="all"):
        return self.movements.axis_length(axis)

    def get_xyz(self):
        return self.movements.get_xyz()

    def check_position(self, user_x, user_y, user_z, tolerance):
        return self.movements.check_position(user_x, user_y, user_z, tolerance)

    # peripherals.py

    def control_servo(self, pin, angle):
        return self.peripherals.control_servo(pin, angle)

    def control_peripheral(self, id, value, mode=None):
        return self.peripherals.control_peripheral(id, value, mode)

    def toggle_peripheral(self, id):
        return self.peripherals.toggle_peripheral(id)

    def on(self, id):
        return self.peripherals.on(id)

    def off(self, id):
        return self.peripherals.off(id)

    # resources.py

    def mark_coord(self, x, y, z, property, mark_as):
        return self.resources.mark_coord(x, y, z, property, mark_as)

    def sequence(self, sequence_id):
        return self.resources.sequence(sequence_id)

    def get_seed_tray_cell(self, tray_id, tray_cell):
        return self.resources.get_seed_tray_cell(tray_id, tray_cell)

    def detect_weeds(self):
        return self.resources.detect_weeds()

    def lua(self, code_snippet):
        return self.resources.lua(code_snippet)

    def if_statement(self, variable, operator, value, then_id, else_id):
        return self.resources.if_statement(variable, operator, value, then_id, else_id)

    # tools.py

    def mount_tool(self, tool_str):
        return self.tools.mount_tool(tool_str)

    def dismount_tool(self):
        return self.tools.dismount_tool()

    def water(self, plant_id):
        return self.tools.water(plant_id)

    def dispense(self, mL, tool_str, pin):
        return self.tools.dispense(mL, tool_str, pin)
