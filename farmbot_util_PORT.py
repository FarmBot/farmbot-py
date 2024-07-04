# farmbot_utilities.py

import json

from farmbot_broker import FarmbotBroker
from farmbot_api import FarmbotAPI

RPC_REQUEST = {
    "kind": "rpc_request",
    "args": {
        "label": ""
    }
}

class Farmbot():
    def __init__(self):
        self.broker = FarmbotBroker()
        self.api = FarmbotAPI()

        self.token = None
        self.error = None

        self.echo = True # Choose whether functions print return statement
        self.verbose = True # Choose how much detail in return statement

    def function_return(self, return_value):
        if self.echo is True:
            return print(return_value)
        else:
            return return_value

    # CONNECTIVITY
    # ├── [✅] get_token()
    # │
    # ├── [✅] connect_broker()
    # └── [✅] disconnect_broker()

    def get_token(self, email, password, server='https://my.farm.bot'):
        token_str = self.api.get_token(email, password, server)

        self.token = self.api.token
        self.error = self.api.error

        self.broker.token = self.token

        return self.function_return(token_str)

    def connect_broker(self):
        self.broker.connect()
        # return ...

    def disconnect_broker(self):
        self.broker.disconnect()
        return self.function_return("Disconnected from message broker.")

    # INFORMATION
    # ├── [✅] get_info()
    # ├── [✅] set_info()
    # │
    # ├── [✅] read_status()
    # ├── [🚫] read_sensor()
    # │
    # └── [🚫] env()

    def get_info(self, endpoint, id=None):
        return self.function_return(self.api.get(endpoint, id))
        # return self.api.get(endpoint, id)...

    def set_info(self, endpoint, field, value, id=None):
        new_value = {
            field: value
        }

        self.api.patch(endpoint, id, new_value)
        return self.function_return(self.api.get(endpoint, id))
        # return self.api.get(endpoint, id)...
    
    def read_status(self):
        status_message = {
            **RPC_REQUEST,
            "body": {
                "kind": "read_status",
                "args": {}
            }
        }

        self.broker.publish(status_message)
        # return ...

    # MESSAGES
    # ├── [✅] log()
    # ├── [✅] message()
    # │
    # ├── [✅] debug()
    # └── [✅] toast()

    def log(self, message, type=None, channel=None):
        log_message = {
            "message": message,
            "type": type,
            "channel": channel # Specifying channel does not do anything
        }

        endpoint = 'logs'
        id = None

        self.api.post(endpoint, id, log_message)
        # return ...

    def message(self, message, type=None, channel=None):
        message_message = {
            **RPC_REQUEST,
            "body": {
                "kind": "send_message",
                "args": {
                    "message": message,
                    "message_type": type
                },
                "body": {
                    "kind": "channel",
                    "args": {
                        "channel_name": channel
                    }
                }
            }
        }

        self.broker.publish(message_message)
        # return ...

    def debug(self, message):
        self.message(message, 'debug')
        # return ...

    def toast(self, message):
        self.message(message, 'toast')
        # return ...

    # LOGIC
    # ├── [✅] wait()
    # ├── [✅] e_stop()
    # ├── [✅] unlock()
    # ├── [✅] reboot()
    # └── [✅] shutdown()

    def wait(self, time):
        wait_message = {
            **RPC_REQUEST,
            "body": {
                "kind": "wait",
                "args": {
                    "milliseconds": time
                }
            }
        }

        self.broker.publish(wait_message)
        return self.function_return("Waiting for "+str(TIME)+" milliseconds...")

    def e_stop(self):
        e_stop_message = {
            **RPC_REQUEST,
            "body": {
                "kind": "emergency_lock",
                "args": {}
            }
        }

        self.broker.publish(e_stop_message)
        return self.function_return("Triggered device emergency stop.")

    def unlock(self):
        unlock_message = {
            **RPC_REQUEST,
            "body": {
                "kind": "emergency_unlock",
                "args": {}
            }
        }

        self.broker.publish(unlock_message)
        return self.function_return("Triggered device unlock.")

    def reboot(self):
        reboot_message = {
            **RPC_REQUEST,
            "body": {
                "kind": "reboot",
                "args": {
                    "package": "farmbot_os"
                }
            }
        }

        self.broker.publish(reboot_message)
        return self.function_return("Triggered device reboot.")

    def shutdown(self):
        shutdown_message = {
            **RPC_REQUEST,
            "body": {
                "kind": "power_off",
                "args": {}
            }
        }

        self.broker.publish(shutdown_message)
        return self.function_return("Triggered device shutdown.")

    # PERIPHERALS
    # ├── [✅] control_servo()
    # ├── [🚫] control_peripheral()
    # ├── [🚫] toggle_peripheral()
    # │
    # ├── [🚫] on()
    # ├── [🚫] off()
    # │
    # ├── [🚫] calibrate_camera()
    # ├── [✅] take_photo()
    # ├── [🚫] photo_grid()
    # │
    # ├── [✅] soil_height()
    # └── [✅] detect_weeds()

    def control_servo(self, pin, angle):
        if angle < 0 or angle > 180:
            return print("ERROR: Servo angle constrained to 0-180 degrees.")
        else:
            control_servo_message = {
                **RPC_REQUEST,
                "body": {
                    "kind": "set_servo_angle",
                    "args": {
                        "pin_number": pin,
                        "pin_value": angle # From 0 to 180
                    }
                }
            }

            self.broker.publish(control_servo_message)
            # return ...

    def take_photo(self):
        take_photo_message = {
            **RPC_REQUEST,
            "body": {
                "kind": "take_photo",
                "args": {}
            }
        }

        self.broker.publish(take_photo_message)
        # return ...

    def soil_height(self):
        soil_height_message = {
            **RPC_REQUEST,
            "body": {
                "kind": "execute_script",
                "args": {
                    "label": "Measure Soil Height"
                }
            }
        }

        self.broker.publish(soil_height_message)
        # return ...

    def detect_weeds(self):
        detect_weeds_message = {
            **RPC_REQUEST,
            "body": {
                "kind": "execute_script",
                "args": {
                    "label": "plant-detection"
                }
            }
        }

        self.broker.publish(detect_weeds_message)
        # return ...

    # MOVEMENT
    # ├── [✅] move()
    # ├── [🚫] get_xyz()
    # ├── [🚫] check_position()
    # │
    # ├── [✅] set_home()
    # ├── [✅] find_home()
    # │
    # ├── [✅] axis_length()
    # ├── [✅] safe_z()
    # │
    # └── [✅] garden_size()

    def move(self, x, y, z):
        def axis_overwrite(axis, value):
            return {
                "kind": "axis_overwrite",
                "args": {
                    "axis": axis,
                    "axis_operand": {
                        "kind": "numeric",
                        "args": {
                            "number": value
                        }
                    }
                }
            }

        move_message = {
            **RPC_REQUEST,
            "body": {
                "kind": "move",
                "args": {},
                "body": [
                    axis_overwrite("x", x),
                    axis_overwrite("y", y),
                    axis_overwrite("z", z)
                ]
            }
        }

        self.broker.publish(move_message)
        # return ...

    def set_home(self, axis='all'):
        set_home_message = {
            **RPC_REQUEST,
            "body": {
                "kind": "zero",
                "args": {
                    "axis": axis
                }
            }
        }

        self.broker.publish(set_home_message)
        # return ...

    def find_home(self, axis='all', speed=100):
        if speed > 100 or speed < 1:
            return print("ERROR: Speed constrained to 1-100.")
        else:
            find_home_message = {
                **RPC_REQUEST,
                "body": {
                    "kind": "find_home",
                    "args": {
                        "axis": axis,
                        "speed": speed
                    }
                }
            }

            self.broker.publish(find_home_message)
            # return ...

    def axis_length(self, axis='all'):
        axis_length_message = {
            **RPC_REQUEST,
            "body": {
                "kind": "calibrate",
                "args": {
                    "axis": axis
                }
            }
        }

        self.broker.publish(axis_length_message)
        # return ...

    def safe_z(self):
        json_data = self.get_info('fbos_config')
        return self.function_return(json_data['safe_height'])
        # return json_data['safe_height']...

    def garden_size(self):
        json_data = self.get_info('firmware_config')

        # Get x axis length in steps
        x_steps = json_data['movement_axis_nr_steps_x']

        # Get number of steps per millimeter on the x axis
        x_mm = json_data['movement_step_per_mm_x']

        # Get y axis length in steps
        y_steps = json_data['movement_axis_nr_steps_y']

        # Get number of steps per millimeter on the y axis
        y_mm = json_data['movement_step_per_mm_y']

        length_x = x_steps / x_mm
        length_y = y_steps / y_mm
        area = length_x * length_y

        size_value = {'x': length_x, 'y': length_y, 'area': area}
        return self.function_return(size_value)

    # COMMANDS
    # ├── [🚫] mark_as()
    # │
    # ├── [✅] group()
    # ├── [✅] curve()
    # │
    # ├── [🚫] verify_tool()
    # ├── [🚫] mount_tool()
    # ├── [🚫] dismount_tool()
    # │
    # ├── [🚫] water()
    # ├── [🚫] dispense()
    # ├── [🚫] sequence()
    # │
    # ├── [🚫] get_seed_tray_call(tray, cell)
    # ├── [🚫] sort(points, method)
    # │
    # ├── [🚫] get_job()
    # ├── [🚫] set_job()
    # └── [🚫] complete_job()

    def group(self, id):
        return self.function_return(self.get_info('point_groups', id))
        # return self.get_info('point_groups', id)...

    def curve(self, id):
        return self.function_return(self.get_info('curves', id))
        # return self.get_info('curves', id)...

    # COMPLEX
    # ├── [✅] assertion()
    # ├── [🚫] if_statement()
    # └── [🚫] lua()

    def assertion(self, code, type, id=''):
        assertion_message = {
            **RPC_REQUEST,
            "body": {
                "kind": "assertion",
                "args": {
                    "lua": code,
                    "_then": {
                        "kind": "execute",
                        "args": {
                            "sequence_id": id # Recovery sequence ID
                        }
                    },
                    "assertion_type": type # If test fails, do this
                }
            }
        }

        self.broker.publish(assertion_message)
        # return ...
