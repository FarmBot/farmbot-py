import json

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

        self.echo = True
        self.verbose = True

    def return_config(self, return_value): # TODO: which functions return json()
        """Configure echo and verbosity of function returns."""

        if self.echo is True and self.verbose is True:
            print('-' * 100)
            print(f'FUNCTION: {return_value}\n')
            return print(return_value)
        elif self.echo is True and self.verbose is False:
            print('-' * 100)
            return print(return_value)
        elif self.echo is False and self.verbose is False:
            return return_value
        else:
            print('-' * 100)
            return print("ERROR: Incompatible return configuration.")

    ## INFORMATION

    def read_status(self):
        """Get Farmbot device status tree via message broker."""

        status_message = {
            **RPC_REQUEST,
            "body": {
                "kind": "read_status",
                "args": {}
            }
        }

        self.broker_connect.publish(status_message)
        self.broker_connect.listen(5, 'status')

        status_tree = self.broker_connect.last_message

        return status_tree

    def read_sensor(self, id):
        """Get sensor data via message broker."""

        peripheral_str = self.api.get_info('peripherals', id)
        mode = peripheral_str['mode']

        read_sensor_message = {
            **RPC_REQUEST,
            "body": [{
                "kind": "read_pin",
                "args": {
                    "pin_mode": mode,
                    "label": '---',
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

        # return ...

    ## MESSAGING

    def message(self, message, type=None, channel=None):
        """Send log message via message broker."""

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
        """Send 'debug' type log message via message broker."""
        self.message(message, 'debug')
        # return ...

    def toast(self, message):
        """Send 'toast' type log message via message broker."""
        self.message(message, 'toast')
        # return ...

    ## BASIC COMMANDS

    def wait(self, duration):
        """Send wait command to device via message broker."""

        wait_message = {
            **RPC_REQUEST,
            "body": {
                "kind": "wait",
                "args": {
                    "milliseconds": duration
                }
            }
        }

        self.broker_connect.publish(wait_message)
        return print("Waiting for "+str(duration)+" milliseconds...")

    def e_stop(self):
        """Send emergency stop command to device via message broker."""

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
        """Send unlock command to device via message broker."""

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
        """Send reboot command to device via message broker."""

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
        """Send shutdown command to device via message broker."""

        shutdown_message = {
            **RPC_REQUEST,
            "body": {
                "kind": "power_off",
                "args": {}
            }
        }

        self.broker_connect.publish(shutdown_message)
        return print("Triggered device shutdown.")

    ## MOVEMENT

    def move(self, x, y, z): # TODO: update for coord(x,y,z)
        """Move to new x, y, z position via message broker."""
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

    def get_xyz(self): # TODO: update for coord(x,y,z)
        """Get current x, y, z coordinate of device via message broker."""

        tree_data = self.read_status()

        position = tree_data["position"]

        x_val = position['x']
        y_val = position['y']
        z_val = position['z']

        return {'x': x_val, 'y': y_val, 'z': z_val}

    def check_position(self, user_x, user_y, user_z, tolerance): # TODO: update for coord(x,y,z)

        user_values = [user_x, user_y, user_z]

        position_data = self.get_xyz()
        actual_vals = [position_data['x'], position_data['y'], position_data['z']]

        for user_value, actual_value in zip(user_values, actual_vals):
            if actual_value - tolerance <= user_value <= actual_value + tolerance:
                print("Farmbot is at position.")
            else:
                print("Farmbot is NOT at position.")

    ## PERIPHERALS

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
        """Toggle peripheral off/on via message broker."""

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
        """Toggle peripheral ON via message broker."""

        peripheral_str = self.api.get_info('peripherals', id)
        mode = peripheral_str['mode']

        if mode == 1:
            self.control_peripheral(id, 255)
        elif mode == 0:
            self.control_peripheral(id, 1)

        # return ...

    def off(self, id):
        """Toggle peripheral OFF via message broker."""

        self.control_peripheral(id, 0)
        # return ...

    ## RESOURCES

    # TODO: sort(points, method) --> API? --> order group of points according to chosen method

    # def sort(tray, tray_cell):
    #     cell = tray_cell.upper()
    #     seeder_needle_offset = 17.5
    #     cell_spacing = 12.5

    #     cells = {
    #         "A1": {"label": "A1", "x": 0, "y": 0},
    #         "A2": {"label": "A2", "x": 0, "y": 1},
    #         "A3": {"label": "A3", "x": 0, "y": 2},
    #         "A4": {"label": "A4", "x": 0, "y": 3},
    #         "B1": {"label": "B1", "x": -1, "y": 0},
    #         "B2": {"label": "B2", "x": -1, "y": 1},
    #         "B3": {"label": "B3", "x": -1, "y": 2},
    #         "B4": {"label": "B4", "x": -1, "y": 3},
    #         "C1": {"label": "C1", "x": -2, "y": 0},
    #         "C2": {"label": "C2", "x": -2, "y": 1},
    #         "C3": {"label": "C3", "x": -2, "y": 2},
    #         "C4": {"label": "C4", "x": -2, "y": 3},
    #         "D1": {"label": "D1", "x": -3, "y": 0},
    #         "D2": {"label": "D2", "x": -3, "y": 1},
    #         "D3": {"label": "D3", "x": -3, "y": 2},
    #         "D4": {"label": "D4", "x": -3, "y": 3}
    #     }

    #     # Checks
    #     if tray["pointer_type"] != "ToolSlot":
    #         print("Error: Seed Tray variable must be a seed tray in a slot")
    #         return
    #     elif cell not in cells:
    #         print("Error: Seed Tray Cell must be one of **A1** through **D4**")
    #         return

    #     # Flip X offsets depending on pullout direction
    #     flip = 1
    #     if tray["pullout_direction"] == 1:
    #         flip = 1
    #     elif tray["pullout_direction"] == 2:
    #         flip = -1
    #     else:
    #         print("Error: Seed Tray **SLOT DIRECTION** must be `Positive X` or `Negative X`")
    #         return

    #     # A1 coordinates
    #     A1 = {
    #         "x": tray["x"] - seeder_needle_offset + (1.5 * cell_spacing * flip),
    #         "y": tray["y"] - (1.5 * cell_spacing * flip),
    #         "z": tray["z"]
    #     }

    #     # Cell offset from A1
    #     offset = {
    #         "x": cell_spacing * cells[cell]["x"] * flip,
    #         "y": cell_spacing * cells[cell]["y"] * flip
    #     }

    #     # Return cell coordinates
    #     return {
    #         "x": A1["x"] + offset["x"],
    #         "y": A1["y"] + offset["y"],
    #         "z": A1["z"]
    #     }

    def soil_height(self):
        """Execute script to check soil height via message broker."""

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
        """Execute script to detect weeds via message broker."""

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

    ## OTHER FUNCTIONS

    def calibrate_camera(self): # TODO: fix "sequence_id"
        calibrate_message = {
            **RPC_REQUEST,
            "body": {
                "kind": "execute_script",
                "args": {
                    "label": "camera-calibration"
                },
                "body": {
                    "kind": "pair",
                    "args": {
                        "label": "CAMERA_CALIBRATION_easy_calibration",
                        "value": "\"TRUE\""
                    }
                }
            }
        }

        self.broker_connect.publish(calibrate_message)
        # return ...

    def photo_grid(self): # TODO: fix "sequence_id"
        photo_grid_message = {
            **RPC_REQUEST,
            "body": {
                "kind": "execute",
                "args": {
                    "sequence_id": 24372
                }
            }
        }

        self.broker_connect.publish(photo_grid_message)
        # return ...

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

    def take_photo(self):
        """Send photo command to camera via message broker."""

        take_photo_message = {
            **RPC_REQUEST,
            "body": {
                "kind": "take_photo",
                "args": {}
            }
        }

        self.broker_connect.publish(take_photo_message)
        # return ...

    def mark_coord(self, x, y, z, property, mark_as): # TODO: Fix "label"
        mark_coord_message = {
            **RPC_REQUEST,
            "body": {
                "kind": "update_resource",
                "args": {
                    "resource": {
                        "kind": "identifier",
                        "args": {
                            "label": "test_location" # What is happening here??
                        }
                    }
                },
                "body": {
                    "kind": "pair",
                    "args": {
                        "label": property,
                        "value": mark_as
                    }
                }
            }
        }

        # return ...

    # TODO: verify_tool() --> get broker message example
    # TODO: mount_tool() --> get broker message example
    # TODO: dismount_tool() --> get broker message example

    # def mount_tool(self, x, y, z):
    #     mount_tool_message = {
    #         **RPC_REQUEST,
    #         "body": {
    #             "kind": "execute",
    #             "body": {
    #                 "kind": "parameter_application",
    #                 "args": {
    #                     "label": "Tool",
    #                     "data_value": {
    #                         "kind": "coordinate",
    #                         "args": {
    #                             "x": x,
    #                             "y": y,
    #                             "z": z
    #                         }
    #                     }
    #                 }
    #             }
    #         }
    #     }

    #     self.broker_connect.publish(mount_tool_message)
    #     # return ...

    # TODO: water() --> all or single coords
    # TODO: dispense() --> single coords?

    # TODO: sequence() --> execute a sequence by ID
    # TODO: get_seed_tray_call(tray, cell) --> get coordinates of cell in seed tray by passing tool object and cell id, eg B3

    # TODO: get_job() --> access status tree --> fetch all or single by name
    # TODO: set_job() --> access status tree --> inject(?) new or edit single by name
    # TODO: complete_job() --> access status tree --> edit single by name

    def lua(self, code_snippet): # TODO: verify working
        lua_message = {
            **RPC_REQUEST,
            "body": {
                "kind": "lua",
                "args": {
                    "lua": code_snippet
                }
            }
        }

        self.broker_connect.publish(lua_message)
        # return ...

    def if_statement(self, variable, operator, value, then_id, else_id): # TODO: add 'do nothing' functionality
        if_statement_message = {
            **RPC_REQUEST,
            "body": {
                "kind": "_if",
                "args": {
                    "lhs": variable,
                    "op": operator,
                    "rhs": value,
                    "_then": {
                        "kind": "execute",
                        "args": {
                            "sequence_id": then_id
                        }
                    },
                    "_else": {
                        "kind": "execute",
                        "args": {
                            "sequence_id": else_id
                        }
                    }
                }
            }
        }

        self.broker_connect.publish(if_statement_message)
        # return ...

    def assertion(self, code, as_type, id=''): # TODO: add 'continue' functionality
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
                    "assertion_type": as_type # If test fails, do this
                }
            }
        }

        self.broker_connect.publish(assertion_message)
        # return ...
