"""
Farmbot class.
"""

from imports import *

class Farmbot():
    def __init__(self):
        self.token = None
        self.error = None

        self.echo = True

    # authentication.py

    def set_token(self, token):
        self.token = token

        # Set API token (redundant--used for tests)
        auth.token = token

        # Set file tokens
        basic.token = token
        broker.token = token
        camera.token = token
        info.token = token
        job.token = token
        message.token = token
        move.token = token
        peripheral.token = token
        resource.token = token
        tool.token = token

    def get_token(self, email, password, server="https://my.farm.bot"):
        # Call get_token() source
        # Set authentication token for all modules

        token_data = auth.get_token(email, password, server)

        self.set_token(auth.token)
        self.error = auth.error

        return token_data

    # basic_commands.py

    def wait(self, duration):
        return basic.wait(duration)

    def e_stop(self):
        return basic.e_stop()

    def unlock(self):
        return basic.unlock()

    def reboot(self):
        return basic.reboot()

    def shutdown(self):
        return basic.shutdown()

    # broker.py

    def connect_broker(self):
        return broker.connect()

    def disconnect_broker(self):
        return broker.disconnect()

    # camera.py

    def calibrate_camera(self):
        return camera.calibrate_camera()

    def take_photo(self):
        return camera.take_photo()

    # information.py

    def get_info(self, endpoint, id=None):
        return info.get_info(endpoint, id)

    def set_info(self, endpoint, field, value, id=None):
        return info.set_info(endpoint, field, value, id)

    def safe_z(self):
        return info.safe_z()

    def garden_size(self):
        return info.garden_size()

    def group(self, id=None):
        return info.group(id)

    def curve(self, id=None):
        return info.curve(id)

    def soil_height(self):
        return info.soil_height()

    def read_status(self):
        return info.read_status()

    def read_sensor(self, id):
        return info.read_sensor(id)

    # jobs.py

    def get_job(self, job_str):
        return job.get_job(job_str)

    def set_job(self, job_str, status_message, value):
        return job.set_job(job_str, status_message, value)

    def complete_job(self, job_str):
        return job.complete_job(job_str)

    # messages.py

    def log(self, message_str, type=None, channel=None):
        return message.log(message_str, type, channel)

    def message(self, message_str, type=None, channel="ticker"):
        return message.message(message_str, type, channel)

    def debug(self, message_str):
        return message.debug(message_str)

    def toast(self, message_str):
        return message.toast(message_str)

    # movements.py

    def move(self, x, y, z):
        return move.move(x, y, z)

    def set_home(self, axis="all"):
        return move.set_home(axis)

    def find_home(self, axis="all", speed=100):
        return move.find_home(axis, speed)

    def axis_length(self, axis="all"):
        return move.axis_length(axis)

    def get_xyz(self):
        return move.get_xyz()

    def check_position(self, user_x, user_y, user_z, tolerance):
        return move.check_position(user_x, user_y, user_z, tolerance)

    # peripherals.py

    def control_servo(self, pin, angle):
        return peripheral.control_servo(pin, angle)

    def control_peripheral(self, id, value, mode=None):
        return peripheral.control_peripheral(id, value, mode)

    def toggle_peripheral(self, id):
        return peripheral.toggle_peripheral(id)

    def on(self, id):
        return peripheral.on(id)

    def off(self, id):
        return peripheral.off(id)

    # resources.py

    def mark_coord(self, x, y, z, property, mark_as):
        return resource.mark_coord(x, y, z, property, mark_as)

    def sequence(self, sequence_id):
        return resource.sequence(sequence_id)

    def get_seed_tray_cell(self, tray_id, tray_cell):
        return resource.get_seed_tray_cell(tray_id, tray_cell)

    def detect_weeds(self):
        return resource.detect_weeds()

    def lua(self, code_snippet):
        return resource.lua(code_snippet)

    def if_statement(self, variable, operator, value, then_id, else_id):
        return resource.if_statement(variable, operator, value, then_id, else_id)

    # tools.py

    def mount_tool(self, tool_str):
        return tool.mount_tool(tool_str)

    def dismount_tool(self):
        return tool.dismount_tool()

    def water(self, plant_id):
        return tool.water(plant_id)

    def dispense(self, mL, tool_str, pin):
        return tool.dispense(mL, tool_str, pin)
