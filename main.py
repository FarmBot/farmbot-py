"""
Farmbot class.
"""

from imports import *

class State():
    def __init__(self):
        self.token = None
        self.error = None
        self.last_message = None

class Farmbot():
    def __init__(self):
        self.state = State()
        self.echo = True

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

    def set_token(self, token):
        self.state.token = token

    def set_echo(self, value):
        if value is True:
            self.echo = True
        elif value is False:
            self.echo = False
        else:
            return print("ERROR: `Echo` can only be True or False.")

    # authentication.py

    def get_token(self, email, password, server="https://my.farm.bot"):
        return self.auth.get_token(email, password, server)

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

    def start_listen(self, channel="#"):
        return self.broker.start_listen(channel)

    def stop_listen(self):
        return self.broker.stop_listen()

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

    def assertion(self, code, as_type, id=""):
        return self.resources.assertion(code, as_type, id)

    # tools.py

    def mount_tool(self, tool_str):
        return self.tools.mount_tool(tool_str)

    def dismount_tool(self):
        return self.tools.dismount_tool()

    def water(self, plant_id):
        return self.tools.water(plant_id)

    def dispense(self, mL, tool_str, pin):
        return self.tools.dispense(mL, tool_str, pin)
