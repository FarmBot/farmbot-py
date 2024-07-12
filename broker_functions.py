from broker_connect import BrokerConnect
from api_functions import ApiFunctions

RPC_REQUEST = {
    "kind": "rpc_request",
    "args": {
        "label": ""
    }
}

class BrokerFunctions():
    def __init__(self):
        self.broker_connect = BrokerConnect()
        self.api = ApiFunctions()

        self.token = None
        self.client = None

    def read_status(self):
        status_message = {
            **RPC_REQUEST,
            "body": {
                "kind": "read_status",
                "args": {}
            }
        }

        self.broker_connect.publish(status_message)
        # return ...

    def read_sensor(self, id, mode, label='---'):
        read_sensor_message = {
            **RPC_REQUEST,
            "body": [{
                "kind": "read_pin",
                "args": {
                    "pin_mode": mode,
                    "label": label,
                    "pin_number": {
                        "kind": "named_pin",
                        "args": {
                            "pin_type": "Peripheral",
                            "pin_id": id
                        }
                    }
                }
            }]
        }

        self.broker_connect.publish(read_sensor_message)
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

        self.broker_connect.publish(message_message)
        # return ...

    def debug(self, message):
        self.message(message, 'debug')
        # return ...

    def toast(self, message):
        self.message(message, 'toast')
        # return ...

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

        self.broker_connect.publish(wait_message)
        return print("Waiting for "+str(time)+" milliseconds...")

    def e_stop(self):
        e_stop_message = {
            **RPC_REQUEST,
            "body": {
                "kind": "emergency_lock",
                "args": {}
            }
        }

        self.broker_connect.publish(e_stop_message)
        return print("Triggered device emergency stop.")

    def unlock(self):
        unlock_message = {
            **RPC_REQUEST,
            "body": {
                "kind": "emergency_unlock",
                "args": {}
            }
        }

        self.broker_connect.publish(unlock_message)
        return print("Triggered device unlock.")

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

        self.broker_connect.publish(reboot_message)
        return print("Triggered device reboot.")

    def shutdown(self):
        shutdown_message = {
            **RPC_REQUEST,
            "body": {
                "kind": "power_off",
                "args": {}
            }
        }

        self.broker_connect.publish(shutdown_message)
        return print("Triggered device shutdown.")

    # calibrate_camera() --> sequence (broker message)
    # photo_grid() --> sequence (broker message)

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

            self.broker_connect.publish(control_servo_message)
            # return ...

    def control_peripheral(self, id, value, mode=None):
        if mode is None:
            peripheral_str = self.api.get_info('peripherals', id)
            mode = peripheral_str['mode']

        control_peripheral_message = {
            **RPC_REQUEST,
            "body": {
                "kind": "write_pin",
                "args": {
                    "pin_value": value, # Controls ON/OFF or slider value from 0-255
                    "pin_mode": mode, # Controls digital (0) or analog (1) mode
                    "pin_number": {
                        "kind": "named_pin",
                        "args": {
                            "pin_type": "Peripheral",
                            "pin_id": id
                        }
                    }
                }
            }
        }

        self.broker_connect.publish(control_peripheral_message)
        # return ...

    def toggle_peripheral(self, id):
        toggle_peripheral_message = {
            **RPC_REQUEST,
            "body": [{
                "kind": "toggle_pin",
                "args": {
                    "pin_number": {
                        "kind": "named_pin",
                        "args": {
                            "pin_type": "Peripheral",
                            "pin_id": id
                        }
                    }
                }
            }]
        }

        self.broker_connect.publish(toggle_peripheral_message)
        # return ...

    def on(self, id):
        peripheral_str = self.api.get_info('peripherals', id)
        mode = peripheral_str['mode']

        if mode == 1:
            self.control_peripheral(id, 255)
        elif mode == 0:
            self.control_peripheral(id, 1)

        # return ...

    def off(self, id):
        self.control_peripheral(id, 0)
        # return ...

    def take_photo(self):
        take_photo_message = {
            **RPC_REQUEST,
            "body": {
                "kind": "take_photo",
                "args": {}
            }
        }

        self.broker_connect.publish(take_photo_message)
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

        self.broker_connect.publish(soil_height_message)
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

        self.broker_connect.publish(detect_weeds_message)
        # return ...

    # get_xyz() --> requires read_status() --> LUA
    # check_position() --> requires read_status() --> LUA

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

        self.broker_connect.publish(move_message)
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

        self.broker_connect.publish(set_home_message)
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

            self.broker_connect.publish(find_home_message)
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

        self.broker_connect.publish(axis_length_message)
        # return ...

    # mark_as() --> sequence (broker message)

    # verify_tool() --> check
    # mount_tool() --> check
    # dismount_tool() --> check

    # water() --> check
    # dispense() --> check

    # sequence() --> check
    # get_seed_tray_call(tray, cell) --> check
    # sort(points, method) --> check (API?)

    # get_job() --> LUA
    # set_job() --> LUA
    # complete_job() --> LUA

    # lua() --> sequence (broker message)
    # if_statement() --> sequence (broker message)

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

        self.broker_connect.publish(assertion_message)
        # return ...
