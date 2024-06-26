# farmbot_utilities.py

import sys
import json
import getpass
import socket
import requests

import paho.mqtt.publish as publish

from functions_BROKER import FarmbotBroker
from functions_API import FarmbotAPI

BROKER = FarmbotBroker()
API = FarmbotAPI()

RPC_REQUEST = {
    "kind": "rpc_request",
    "args": {
        "label": ""
    }
}

class Farmbot():
    def __init__(self):
        print("")

    def token(self, EMAIL, PASSWORD, SERVER):
        self.error = API.error
        self.token = API.get_token(EMAIL, PASSWORD, SERVER)
        return self.token

    def get_info(self, ENDPOINT, ID=''):
        return API.get(ENDPOINT, ID)

    def set_info(self, ENDPOINT, FIELD, VALUE, ID=''):
        new_value = {
            FIELD: VALUE
        }

        API.patch(ENDPOINT, ID, new_value)

    def new_log(self, MESSAGE, TYPE, CHANNEL='ticker', VERBOSITY='2'):
        ENDPOINT = 'logs'
        ID = ''

        new_log_message = {
            "message": MESSAGE,
            "type": TYPE,
            "channel": CHANNEL, # Specifying channel does not do anything
            "verbosity": VERBOSITY
        }

        API.post(ENDPOINT, ID, new_log_message)

    def send_message(self, MESSAGE, TYPE, CHANNEL=''):
        send_message_message = {
            **RPC_REQUEST,
            "body": [{
                "kind": "send_message",
                "args": {
                    "message": MESSAGE,
                    "message_type": TYPE
                },
                "body": [{
                    "kind": "channel",
                    "args": {
                        "channel_name": CHANNEL
                    }
                }]
            }]
        }

        BROKER.publish(send_message_message)

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

        BROKER.publish(move_message)

    def set_home(self, AXIS='all'):
        set_home_message = {
            **RPC_REQUEST,
            "body": [{
                "kind": "zero",
                "args": {
                    "axis": AXIS
                }
            }]
        }

        BROKER.publish(set_home_message)

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

        BROKER.publish(find_home_message)

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

        BROKER.publish(axis_length_message)

    def control_servo(self, PIN, ANGLE):
        control_servo_message = {
            **RPC_REQUEST,
            "body": [{
                "kind": "set_servo_angle",
                "args": {
                    "pin_number": PIN,
                    "pin_value": ANGLE # From 0 to 180 (add restriction?)
                }
            }]
        }

        BROKER.publish(control_servo_message)

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

        BROKER.publish(control_peripheral_message)

    def toggle_peripheral(self, ID):
        toggle_peripheral_message = {
            **RPC_REQUEST,
            "body": [{
                "kind": "toggle_pin",
                "args": {
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

        BROKER.publish(toggle_peripheral_message)

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

        BROKER.publish(read_sensor_message)

    def take_photo(self):
        take_photo_message = {
            **RPC_REQUEST,
            "body": [{
                "kind": "take_photo",
                "args": {}
            }]
        }

        BROKER.publish(take_photo_message)

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

        BROKER.publish(detect_weeds_message)

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

        BROKER.publish(soil_height_message)

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

        BROKER.publish(wait_message)

    def if_statement(self, VARIABLE, ID, OPERATOR, VALUE, THEN_ID, ELSE_ID):
        if VARIABLE == 'position':
            define_args = {
                "lhs": ID
            }
        elif VARIABLE == 'peripheral':
            define_args = {
                "lhs": {
                    "kind": "named_pin",
                    "args": {
                        "pin_type": "Peripheral",
                        "pin_id": ID
                    }
                }
            }
        else:
            return print("The specified variable does not exist...")

        if_statement_message = {
            **RPC_REQUEST,
            "body": [{
                "kind": "_if",
                "args": {
                    **define_args,
                    "op": OPERATOR,
                    "rhs": VALUE,
                    "_then": {
                        "kind": "execute",
                        "args": {
                            "sequence_id": THEN_ID
                        }
                    },
                    "_else": {
                        "kind": "execute",
                        "args": {
                            "sequence_id": ELSE_ID
                        }
                    }
                }
            }]
        }

        BROKER.publish(if_statement_message)

    def e_stop(self):
        e_stop_message = {
            **RPC_REQUEST,
            "body": [{
                "kind": "emergency_lock",
                "args": {}
            }]
        }

        BROKER.publish(e_stop_message)

    def unlock(self):
        unlock_message = {
            **RPC_REQUEST,
            "body": [{
                "kind": "emergency_unlock",
                "args": {}
            }]
        }

        BROKER.publish(unlock_message)

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

        BROKER.publish(reboot_message)

    def shutdown(self):
        shutdown_message = {
            **RPC_REQUEST,
            "body": [{
                "kind": "power_off",
                "args": {}
            }]
        }

        BROKER.publish(shutdown_message)

    def assertion(self, CODE, TYPE, ID=''):
        assertion_message = {
            **RPC_REQUEST,
            "body": [{
                "kind": "assertion",
                "args": {
                    "lua": CODE,
                    "_then": {
                        "kind": "execute",
                        "args": {
                            "sequence_id": ID # Recovery sequence ID
                        }
                    },
                    "assertion_type": TYPE # If test fails, do this
                }
            }]
        }

    def lua(self, CODE):
        lua_message = {
            **RPC_REQUEST,
            "body": [{
                "kind": "lua",
                "args": {
                    "lua": {CODE}
                }
            }]
        }

        BROKER.publish(lua_message)
