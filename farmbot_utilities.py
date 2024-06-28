# farmbot_utilities.py

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
        self.token = None
        self.error = None
        self.broker = FarmbotBroker()
        self.api = FarmbotAPI()

    def get_token(self, EMAIL, PASSWORD, SERVER='https://my.farm.bot'):
        token_string = self.api.get_token(EMAIL, PASSWORD, SERVER)

        self.token = self.api.token
        self.error = self.api.error
        self.broker.token = self.token

        return token_string

    # bot.connect_broker()

    def connect_broker(self):
        self.broker.connect()
        # return print("Connected to message broker.")?

    # bot.disconnect_broker()

    def disconnect_broker(self):
        self.broker.disconnect()
        # return print("Disconnected from message broker.")?

    # bot.get_info('device')
    # bot.get_info('peripherals', '21240')
    # bot.get_info('peripherals', '21240', 'label')

    def get_info(self, ENDPOINT, ID=None, FIELD=None):
        return self.api.get(ENDPOINT, ID, FIELD)

    # bot.set_info('device', 'name', 'Carrot Commander')
    # bot.set_info('peripherals', '21240', 'label', 'Lights')

    def set_info(self, ENDPOINT, FIELD, VALUE, ID=None):
        new_value = {
            FIELD: VALUE
        }

        self.api.patch(ENDPOINT, ID, new_value)
        return self.api.get(ENDPOINT, ID, FIELD)

    # bot.new_log('👋 Hello world!')
    # bot.send_message('🚨 This is a warning...', 'warning', 'toast')

    def new_log(self, MESSAGE, TYPE='success', CHANNEL='toast'):
        ENDPOINT='logs'
        ID=''

        new_log_message = {
            "message": MESSAGE,
            "type": TYPE,
            "channel": CHANNEL, # Specifying channel does not do anything
        }

        self.api.post(ENDPOINT, ID, new_log_message)

    # bot.send_message('👋 Hello world!')
    # bot.send_message('🚨 This is a warning...', 'warning', 'toast')

    def send_message(self, MESSAGE, TYPE='success', CHANNEL='toast'):
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

        self.broker.publish(send_message_message)

    # bot.move(x,y,z)

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

        self.broker.publish(move_message)

    # bot.set_home()
    # bot.set_home('x')

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

        self.broker.publish(set_home_message)

    # bot.find_home()
    # bot.find_home('x')
    # bot.find_home('x',50) with max speed?

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

        self.broker.publish(find_home_message)

    # bot.find_axis_length()
    # bot.find_axis_length('x')

    def find_axis_length(self, AXIS='all'):
        find_axis_length_message = {
            **RPC_REQUEST,
            "body": [{
                "kind": "calibrate",
                "args": {
                    "axis": AXIS
                }
            }]
        }

        self.broker.publish(find_axis_length_message)

    def control_servo(self, PIN, ANGLE):
        if ANGLE < 0 or ANGLE > 180:
            return print("Servo angle constrained to 0-180 degrees.")
        else:
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

            self.broker.publish(control_servo_message)

    # bot.control_peripheral('21240', 1)
    # bot.control_peripheral('21240', 0, digital)

    def control_peripheral(self, ID, VALUE, MODE=None):
        if MODE == None:
            MODE = self.get_info('peripherals', ID, 'mode')
        else:
            MODE = MODE

        # VALUE = ON/OFF where ON = 1 and OFF = 0
        # MODE = DIGITAL/ANALOG where DIGITAL = 0 (ON/OFF) and ANALOG = 1 (RANGE)

        # Changes for pin/not pin and LEDs change pin_type --> BoxLedx...
        control_peripheral_message = {
            **RPC_REQUEST,
            "body": [{
                "kind": "write_pin",
                "args": {
                    "pin_value": VALUE, # Controls ON/OFF or slider value from 0-255
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

        self.broker.publish(control_peripheral_message)

    # bot.toggle('21240')

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

        self.broker.publish(toggle_peripheral_message)

    # bot.read_sensor('21240')

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

        self.broker.publish(read_sensor_message)
        # "Read" sensor... what gets "read"/output?

    # bot.take_photo()

    def take_photo(self):
        take_photo_message = {
            **RPC_REQUEST,
            "body": [{
                "kind": "take_photo",
                "args": {}
            }]
        }

        self.broker.publish(take_photo_message)

    # bot.detect_weeds()

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

        self.broker.publish(detect_weeds_message)
        # returns what? array of weeds?

    # bot.soil_height()

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

        self.broker.publish(soil_height_message)
        # returns what? soil height value(s)?

    # bot.wait(30000)

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

        self.broker.publish(wait_message)
        return print("Waiting for "+str(TIME)+" milliseconds...")

    def if_statement(self, VARIABLE, ID, OPERATOR, VALUE, THEN_ID, ELSE_ID):
        # Positions
        # peripherals
        # pins
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

        self.broker.publish(if_statement_message)

    # bot.e_stop()

    def e_stop(self):
        e_stop_message = {
            **RPC_REQUEST,
            "body": [{
                "kind": "emergency_lock",
                "args": {}
            }]
        }

        self.broker.publish(e_stop_message)
        # return print("device emergency stop")?

    # bot.unlock()

    def unlock(self):
        unlock_message = {
            **RPC_REQUEST,
            "body": [{
                "kind": "emergency_unlock",
                "args": {}
            }]
        }

        self.broker.publish(unlock_message)
        # return print("device unlocked")?

    # bot.reboot()

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

        self.broker.publish(reboot_message)
        # return "device rebooting..."?
        # return "device successfully rebooted"?

    # bot.shutdown()

    def shutdown(self):
        shutdown_message = {
            **RPC_REQUEST,
            "body": [{
                "kind": "power_off",
                "args": {}
            }]
        }

        self.broker.publish(shutdown_message)

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

    # def lua(self, CODE):
    #     lua_message = {
    #         **RPC_REQUEST,
    #         "body": [{
    #             "kind": "lua",
    #             "args": {
    #                 "lua": {CODE}
    #             }
    #         }]
    #     }

    #     self.broker.publish(lua_message)

    # env(key, value?)
    # env(DO, KEY, VALUE=None, CHANGE=None)
        # Gets and sets api/farmware_envs
        # Basically a shortcut to get/set_info(farmware_envs, ID)

    # garden_size()
        # Shortcut to get ALL axis lenghths
        # Calculated from movement_axis_nr_steps_x and movement_step_per_mm_x from api/firmware_config
    def garden_size(self):
        x_steps = self.get_info('firmware_config', 'movement_axis_nr_steps_x')
        x_mm = self.get_info('firmware_config', 'movement_step_per_mm_x')

        y_steps = self.get_info('firmware_config', 'movement_axis_nr_steps_y')
        y_mm = self.get_info('firmware_config', 'movement_step_per_mm_y')
        
        length_x = (x_steps / x_mm)
        length_y = (y_steps / y_mm)

        area = (length_x * length_y)
        
        return {'x': length_x, 'y': length_y, 'area': area}

    # group(ID) = shortcut to get_info(point_groups, ID)
    def group(self, ID):
        return self.get_info('point_groups', ID)

    # safe_z() = shortcut to safe_height value from api/fbos_config
    def safe_z(self):
        return self.get_info('fbos_config', 'safe_height')

    # curve(ID) = shortcut to get_info(curves, ID)
    def curve(self, ID):
        return self.get_info('curves', ID)

    # set_job()
    # get_job()
    # complete_job()

    # debug() = shortcut for specific type of send_message
    def debug(self, MESSAGE):
        self.send_message(MESSAGE, 'debug')

    # toast() = shortcut for specific type of send_message
    def toast(self, MESSAGE):
        self.send_message(MESSAGE, 'toast')

    # go_to_home() = shortcut for move()
    def go_to_home(self, AXIS="all"):
        go_to_home_message = {
            **RPC_REQUEST,
            "body": [{
                "kind": "lua",
                "args": {
                    "lua": {
                        go_to_home(AXIS)
                    }
                }
            }]
        }

        self.broker.publish(go_to_home_message)

    # on() and off() = shortcuts for control_peripheral()
    def on(self, ID):
        mode = self.get_info('peripherals', ID, 'mode')

        if mode == 1:
            self.control_peripheral(ID, 255)
        elif mode == 0:
            self.control_peripheral(ID, 1)

    def off(self, ID):
        self.control_peripheral(ID, 0)

    # read_status() = shortcut to get FarmBot state tree via message broker
    # def read_status(self):
    #     status_message = {
    #         **RPC_REQUEST,
    #         "body": [{
    #             "kind": "read_status",
    #             "args": {}
    #         }]
    #     }

    #     BROKER.publish(status_message)
    #     return output state tree contents

    # check_position(coordinate, tolerance)
        # Requires read_status()

    # get_xyz()
        # Gets current bot position
        # Requires read_status()