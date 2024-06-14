import sys
import json
import requests
from getpass import getpass # Required for authorization token
import paho.mqtt.publish as publish # Required for message broker

RPC_REQUEST = {
    "kind": "rpc_request",
    "args": {
        "label": ""
    }
}

class Farmbot():
    def __init__(self):
        self.token = None

    def get_token(self, EMAIL, PASSWORD, SERVER='https://my.farm.bot'):
        headers = {'content-type': 'application/json'}
        user = {'user': {'email': EMAIL, 'password': PASSWORD}}
        response = requests.post(f'{SERVER}/api/tokens', headers=headers, json=user)
        self.token = response.json()

    def check_token(self):
        if self.token is None:
            print('ERROR: You have no token, please call `get_token` using your login credentials and the server you wish to connect to.')
            sys.exit(1)

    def publish_BROKER(self, PAYLOAD):
        self.check_token()

        publish.single(
            f'bot/{self.token['token']['unencoded']['bot']}/from_clients',
            payload=json.dumps(PAYLOAD),
            hostname=self.token['token']['unencoded']['mqtt'],
            auth={
                'username': self.token['token']['unencoded']['bot'],
                'password': self.token['token']['encoded']
            }
        )

    def API_get(self, URL):
        self.check_token()

        url = f'https:{self.token['token']['unencoded']['iss']}/api/'+URL
        headers = {'authorization': self.token['token']['encoded'], 'content-type': 'application/json'}
        response = requests.get(url, headers=headers)

        # Error messages for specific cases
        error_messages = {
            404: "Invalid Endpoint: The specified endpoint does not exist.",
            400: "Invalid Resource ID: The specified ID is invalid or you do not have access to it.",
            401: "Bad Authentication: The user's token has expired or is invalid.",
            502: "No Internet Connection: Please check your internet connection and try again."
        }

        # Check for successful response
        if response.status_code == 200:
            return json.dumps(response.json(), indent=2)
        # Handle client error (4xx)
        elif 400 <= response.status_code < 500:
            if response.status_code in error_messages:
                return json.dumps(f"Client error {response.status_code} {error_messages[response.status_code]}", indent=2)
            return json.dumps(f"Client error {response.status_code}: {response.reason}", indent=2)
        # Handle server error (5xx)
        elif 500 <= response.status_code < 600:
            if response.status_code in error_messages:
                return json.dumps(f"Client error {response.status_code} {error_messages[response.status_code]}", indent=2)
            return json.dumps(f"Server error {response.status_code}: {response.text}", indent=2)
        else:
            return json.dumps(f"Unexpected error {response.status_code}: {response.text}", indent=2)

    def API_post(self, URL, PAYLOAD):
        self.check_token()

        url = f'https:{self.token['token']['unencoded']['iss']}/api/'+URL
        headers = {'authorization': self.token['token']['encoded'], 'content-type': 'application/json'}
        response = requests.post(url, headers=headers, data=json.dumps(PAYLOAD))

    def API_patch(self, URL, PAYLOAD):
        self.check_token()

        url = f'https:{self.token['token']['unencoded']['iss']}/api/'+URL
        headers = {'authorization': self.token['token']['encoded'], 'content-type': 'application/json'}
        response = requests.patch(url, headers=headers, data=json.dumps(PAYLOAD))

    def reboot(self):
        reboot_message = {
            **RPC_REQUEST,
            "body": [{
                "kind": "reboot",
                "args": {
                    "package": "farmbot_os"
                }
            }]
        }

        self.publish_BROKER(reboot_message)

    def shutdown(self):
        shutdown_message = {
            **RPC_REQUEST,
            "body": [{
                "kind": "power_off",
                "args": {}
            }]
        }

        self.publish_BROKER(shutdown_message)

    def e_stop(self):
        e_stop_message = {
            **RPC_REQUEST,
            "body": [{
                "kind": "emergency_lock",
                "args": {}
            }]
        }

        self.publish_BROKER(e_stop_message)

    def unlock(self):
        unlock_message = {
            **RPC_REQUEST,
            "body": [{
                "kind": "emergency_unlock",
                "args": {}
            }]
        }

        self.publish_BROKER(unlock_message)

    def wait(self, TIME):
        wait_message = {
            **RPC_REQUEST,
            "body": [{
                "kind": "wait",
                "args": {
                    "milliseconds": TIME
                }
            }]
        }

        self.publish_BROKER(wait_message)

    # def mark_as

    def get_info(self, ENDPOINT, ID=''):
        # EXAMPLE: get_info('device') will output all info about your device
        # EXAMPLE: get_info('peripherals', 12345) will output info ONLY about peripheral with ID '12345'
        target_url = ENDPOINT+'/'+ID

        return self.API_get(target_url)

    def edit_info(self, ENDPOINT, FIELD, VALUE, ID=''):
        # EXAMPLE: edit_info('device', 'name', 'Carrot Commander') will rename your device 'Carrot Commander'
        # EXAMPLE: edit_info('peripherals', 'label', 'Camera 2', 12345) will change the label of peripheral with ID '12345' to 'Camera 2'
        target_url = ENDPOINT+'/'+ID
        new_value = {
            FIELD: VALUE
        }

        self.API_patch(target_url, new_value)

    def new_log_API(self, MESSAGE, TYPE):
        target_url = 'logs'
        new_log = {
            "message": MESSAGE,
            "type": TYPE
        }

        self.API_post(target_url, new_log)

    def new_log_BROKER(self, MESSAGE, TYPE):
        new_log = {
            **RPC_REQUEST,
            "body": [{
                "kind": "send_message",
                "args": {
                    "message": MESSAGE,
                    "message_type": TYPE
                }
            }]
        }

        self.publish_BROKER(new_log)

    def move(self, X, Y, Z):
        def axis_overwrite(AXIS, VALUE):
            return {
                "kind": "axis_overwrite",
                "args": {
                    "axis": AXIS,
                    "axis_operand": {
                        "kind": "numeric",
                        "args": {
                            "number": VALUE
                        }
                    }
                }
            }

        move_message = {
            **RPC_REQUEST,
            "body": [{
                "kind": "move",
                "args": {},
                "body": [
                    axis_overwrite("x", X),
                    axis_overwrite("y", Y),
                    axis_overwrite("z", Z)
                ]
            }]
        }

        self.publish_BROKER(move_message)

    def set_home(self, AXIS='all'):
        # EXAMPLE: set_home() will set all current (x,y,z) coords as 'home'
        # EXAMPLE: set_home('x') will set ONLY current x coord as 'home'
        set_home_message = {
            **RPC_REQUEST,
            "body": [{
                "kind": "zero",
                "args": {
                    "axis": AXIS
                }
            }]
        }

        self.publish_BROKER(set_home_message)

    def find_home(self, AXIS='all', SPEED=100):
        find_home_message = {
            **RPC_REQUEST,
            "body": [{
                "kind": "find_home",
                "args": {
                    "axis": AXIS,
                    "speed": SPEED
                }
            }]
        }

        self.publish_BROKER(find_home_message)

    def axis_length(self, AXIS='all'):
        axis_length_message = {
            **RPC_REQUEST,
            "body": [{
                "kind": "calibrate",
                "args": {
                    "axis": AXIS
                }
            }]
        }

        self.publish_BROKER(axis_length_message)

    def control_servo(self, PIN, ANGLE):
        control_servo_message = {
            **RPC_REQUEST,
            "body": [{
                "kind": "set_servo_angle",
                "args": {
                    "pin_number": PIN,
                    "pin_value": ANGLE # From 0 to 180
                }
            }]
        }

        self.publish_BROKER(control_servo_message)

    def control_peripheral(self, ID, VALUE, MODE):
        control_peripheral_message = {
            **RPC_REQUEST,
            "body": [{
                "kind": "write_pin",
                "args": {
                    "pin_value": VALUE, # Controls ON/OFF or slider value
                    "pin_mode": MODE, # Controls digital or analog mode
                    "pin_number": {
                        "kind": "named_pin",
                        "args": {
                            "pin_type": "Peripheral",
                            "pin_id": ID
                        }
                    }
                }
            }]
        }

        self.publish_BROKER(control_peripheral_message)

    def read_sensor(self, ID, MODE, LABEL='---'):
        read_sensor_message = {
            **RPC_REQUEST,
            "body": [{
                "kind": "read_pin",
                "args": {
                    "pin_mode": MODE,
                    "label": LABEL,
                    "pin_number": {
                        "kind": "named_pin",
                        "args": {
                            "pin_type": "Peripheral",
                            "pin_id": ID
                        }
                    }
                }
            }]
        }

        self.publish_BROKER(read_sensor_message)

    def take_photo(self):
        take_photo_message = {
            **RPC_REQUEST,
            "body": [{
                "kind": "take_photo",
                "args": {}
            }]
        }

        self.publish_BROKER(take_photo_message)

    def detect_weeds(self):
        detect_weeds_message = {
            **RPC_REQUEST,
            "body": [{
                "kind": "execute_script",
                "args": {
                    "label": "plant-detection"
                }
            }]
        }

        self.publish_BROKER(detect_weeds_message)

    def soil_height(self):
        soil_height_message = {
            **RPC_REQUEST,
            "body": [{
                "kind": "execute_script",
                "args": {
                    "label": "Measure Soil Height"
                }
            }]
        }

        self.publish_BROKER(soil_height_message)
