from api_functions import ApiFunctions
from broker_functions import BrokerFunctions

class Farmbot():
    def __init__(self):
        self.api = ApiFunctions()
        self.broker = BrokerFunctions()

        self.token = None

    ## SETUP

    def get_token(self, email, password, server="https://my.farm.bot"):
        """Fetch user authentication token via API."""

        token_data = self.api.get_token(email, password, server)

        self.token = token_data

        # Set broker tokens
        self.broker.broker_connect.token = self.api.api_connect.token
        self.broker.api.api_connect.token = self.api.api_connect.token

        return token_data

    def connect_broker(self):
        """Establish persistent connection with message broker."""
        self.broker.broker_connect.connect()

    def disconnect_broker(self):
        """Disconnect from the message broker."""
        self.broker.broker_connect.disconnect()

    def listen_broker(self, duration, channel='#'):
        """Listen to messages via message broker."""
        self.broker.broker_connect.listen(duration, channel)

    ## INFORMATION

    def get_info(self, endpoint, id=None):
        return self.api.get_info(endpoint, id)

    def set_info(self, endpoint, field, value, id=None):
        return self.api.set_info(endpoint, field, value, id)

    def env(self, id=None, field=None, new_val=None):
        return self.api.env(id, field, new_val)

    def group(self, id):
        return self.api.group(id)

    def curve(self, id):
        return self.api.curve(id)

    def read_status(self):
        return self.broker.read_status()

    def read_sensor(self, id):
        return self.broker.read_sensor(id)

    def safe_z(self):
        return self.api.safe_z()

    def garden_size(self):
        return self.api.garden_size()

    ## MESSAGING

    def log(self, message, type=None, channel=None):
        return self.api.log(message, type, channel)

    def message(self, message, type=None, channel=None):
        return self.broker.message(message, type, channel)

    def debug(self, message):
        return self.broker.debug(message)

    def toast(self, message):
        return self.broker.toast(message)

    ## BASIC COMMANDS

    def wait(self, time):
        return self.broker.wait(time)

    def e_stop(self):
        return self.broker.e_stop()

    def unlock(self):
        return self.broker.unlock()

    def reboot(self):
        return self.broker.reboot()

    def shutdown(self):
        return self.broker.shutdown()

    ## MOVEMENT

    def move(self, x, y, z):
        return self.broker.move(x, y, z)

    def set_home(self, axis='all'):
        return self.broker.set_home(axis)

    def find_home(self, axis='all', speed=100):
        return self.broker.find_home(axis, speed)

    def axis_length(self, axis='all'):
        return self.broker.axis_length(axis)

    ## PERIPHERALS

    def control_peripheral(self, id, value, mode=None):
        return self.broker.control_peripheral(id, value, mode)

    def toggle_peripheral(self, id):
        return self.broker.toggle_peripheral(id)

    def on(self, id):
        return self.broker.on(id)

    def off(self, id):
        return self.broker.off(id)

    ## BROKER COMMANDS

    def calibrate_camera(self):
        return self.broker.calibrate_camera()

    def control_servo(self, pin, angle):
        return self.broker.control_servo(pin, angle)

    def take_photo(self):
        return self.broker.take_photo()

    def soil_height(self):
        return self.broker.soil_height()

    def detect_weeds(self):
        return self.broker.detect_weeds()

    def assertion(self, code, as_type, id=''):
        return self.broker.assertion(code, as_type, id)
