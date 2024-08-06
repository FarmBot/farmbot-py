import json
from datetime import datetime

from broker_connect import BrokerConnect
from api_functions import ApiFunctions

RPC_REQUEST = {
    "kind": "rpc_request",
    "args": {
        "label": ""
    }
}

"""MESSAGE TEMPLATE

    message = {
            "kind": "rpc_request",
            "args": {
                "label": "",
                "priority": # Code here... (600)
            },
            "body": [
                {
                    # Instructions here...
                }
            ]
        }

"""

class BrokerFunctions():
    def __init__(self):
        self.broker_connect = BrokerConnect()
        self.api = ApiFunctions()

        self.client = None

    def read_status(self):
        # Get device status tree
        message = {
            "kind": "rpc_request",
            "args": {
                "label": "",
                "priority": 600
            },
            "body": [{
                    "kind": "read_status",
                    "args": {}
            }]
        }

        self.broker_connect.publish(message)
        self.broker_connect.listen(5, 'status')

        status_tree = self.broker_connect.last_message

        # Return status as json object: status[""]
        return status_tree

    def read_sensor(self, id):
        # Get sensor data
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

        # Return sensor as json object: sensor[""]

    def message(self, message, type=None, channel="ticker"):
        message = {
            "kind": "rpc_request",
            "args": {
                "label": "",
                "priority": 600
            },
            "body": [{
                "kind": "send_message",
                "args": {
                    "message": message,
                    "message_type": type
                },
                "body": [{
                    "kind": "channel",
                    "args": {
                        "channel_name": channel
                    }
                }]
            }]
        }

        self.broker_connect.publish(message)
        # No inherent return value

    def debug(self, message):
        # Send 'debug' type message
        self.message(message, "debug", "ticker")
        # No inherent return value

    def toast(self, message):
        # Send 'toast' type message
        self.message(message, "info", "toast")
        # No inherent return value

    def wait(self, duration):
        # Tell bot to wait for some time
        message = {
            "kind": "rpc_request",
            "args": {
                "label": "",
                "priority": 600
            },
            "body": [{
                "kind": "wait",
                "args": {
                    "milliseconds": duration
                }
            }]
        }
        self.broker_connect.publish(message)

        # No inherent return value
        return print("Waiting for "+str(duration)+" milliseconds...")

    def e_stop(self):
        # Tell bot to emergency stop
        new_message = {
            "kind": "rpc_request",
            "args": {
                "label": "",
                "priority": 9000
            },
            "body": [{
                "kind": "emergency_lock",
                "args": {}
            }]
        }
        self.broker_connect.publish(new_message)

        # No inherent return value
        return print("Triggered device emergency stop.")

    def unlock(self):
        # Tell bot to unlock
        message = {
            "kind": "rpc_request",
            "args": {
                "label": "",
                "priority": 9000
            },
            "body": [{
                "kind": "emergency_unlock",
                "args": {}
            }]
        }
        self.broker_connect.publish(message)

        # No inherent return value
        return print("Triggered device unlock.")

    def reboot(self):
        # Tell bot to reboot
        # No inherent return value
        reboot_message = {
            **RPC_REQUEST,
            "body": [{
                "kind": "reboot",
                "args": {
                    "package": "farmbot_os"
                }
            }]
        }

        self.broker_connect.publish(reboot_message)
        return print("Triggered device reboot.")

    def shutdown(self):
        # Tell bot to shutdown
        # No inherent return value
        shutdown_message = {
            **RPC_REQUEST,
            "body": [{
                "kind": "power_off",
                "args": {}
            }]
        }

        self.broker_connect.publish(shutdown_message)
        return print("Triggered device shutdown.")

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

        # Tell bot to move to new xyz coord
        move_message = {
            "kind": "rpc_request",
            "args": {
                "label": "",
                "priority": 600
            },
            "body": [{
                "kind": "move",
                "args": {},
                "body": [
                    axis_overwrite("x", x),
                    axis_overwrite("y", y),
                    axis_overwrite("z", z)
                ]
            }]
        }

        self.broker_connect.publish(move_message)
        # Return new xyz position as values

    def set_home(self, axis='all'):
        # Set current xyz coord as 0,0,0
        set_home_message = {
            "kind": "rpc_request",
            "args": {
                "label": "",
                "priority": 600
            },
            "body": [{
                "kind": "zero",
                "args": {
                    "axis": axis
                }
            }]
        }

        self.broker_connect.publish(set_home_message)
        # No inherent return value

    def find_home(self, axis='all', speed=100):
        # Move to 0,0,0
        if speed > 100 or speed < 1:
            return print("ERROR: Speed constrained to 1-100.")
        else:
            message = {
                "kind": "rpc_request",
                "args": {
                    "label": "",
                    "priority": 600
                },
                "body": [{
                    "kind": "find_home",
                    "args": {
                        "axis": axis,
                        "speed": speed
                    }
                }]
            }
            self.broker_connect.publish(message)

        # Return new xyz position as values

    def axis_length(self, axis='all'):
        # Get axis length
        # Return axis length as values
        axis_length_message = {
            **RPC_REQUEST,
            "body": [{
                "kind": "calibrate",
                "args": {
                    "axis": axis
                }
            }]
        }

        self.broker_connect.publish(axis_length_message)

    def get_xyz(self):
        # Get current xyz coord
        tree_data = self.read_status()

        position = tree_data["position"]

        x_val = position['x']
        y_val = position['y']
        z_val = position['z']

        # Return xyz position as values
        return x_val, y_val, z_val

    def check_position(self, user_x, user_y, user_z, tolerance):
        # Check current xyz coord = user xyz coord within tolerance
        # Return in or out of tolerance range
        user_values = [user_x, user_y, user_z]

        position = self.get_xyz()
        actual_vals = list(position)

        for user_value, actual_value in zip(user_values, actual_vals):
            if actual_value - tolerance <= user_value <= actual_value + tolerance:
                print("Farmbot is at position.")
            else:
                print("Farmbot is NOT at position.")

    def control_peripheral(self, id, value, mode=None):
        # Change peripheral values
        # No inherent return value
        if mode is None:
            peripheral_str = self.api.get_info('peripherals', id)
            mode = peripheral_str['mode']

        control_peripheral_message = {
            **RPC_REQUEST,
            "body": [{
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
            }]
        }

        self.broker_connect.publish(control_peripheral_message)

    def toggle_peripheral(self, id):
        # Toggle peripheral on or off
        # Return status
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

    def on(self, id):
        # Set peripheral to on
        # Return status
        peripheral_str = self.api.get_info("peripherals", id)
        mode = peripheral_str["mode"]

        if mode == 1:
            self.control_peripheral(id, 255)
        elif mode == 0:
            self.control_peripheral(id, 1)

    def off(self, id):
        # Set peripheral to off
        # Return status
        self.control_peripheral(id, 0)

    # TODO: sort_points(points, method)
    # TODO: sort(points, method)

    def soil_height(self):
        # Execute soil height scripts
        # Return soil height as value
        soil_height_message = {
            **RPC_REQUEST,
            "body": [{
                "kind": "execute_script",
                "args": {
                    "label": "Measure Soil Height"
                }
            }]
        }

        self.broker_connect.publish(soil_height_message)

    def detect_weeds(self):
        # Execute detect weeds script
        # Return array of weeds with xyz coords
        detect_weeds_message = {
            **RPC_REQUEST,
            "body": [{
                "kind": "execute_script",
                "args": {
                    "label": "plant-detection"
                }
            }]
        }

        self.broker_connect.publish(detect_weeds_message)


    # TODO: calibrate_camera()
    # TODO: photo_grid()

    def take_photo(self):
        # Take single photo
        # No inherent return value
        take_photo_message = {
            **RPC_REQUEST,
            "body": [{
                "kind": "take_photo",
                "args": {}
            }]
        }

        self.broker_connect.publish(take_photo_message)

    def control_servo(self, pin, angle):
        # Change servo values
        # No inherent return value
        if angle < 0 or angle > 180:
            return print("ERROR: Servo angle constrained to 0-180 degrees.")
        else:
            control_servo_message = {
                **RPC_REQUEST,
                "body": [{
                    "kind": "set_servo_angle",
                    "args": {
                        "pin_number": pin,
                        "pin_value": angle # From 0 to 180
                    }
                }]
            }

            self.broker_connect.publish(control_servo_message)

    def mark_coord(self, x, y, z, property, mark_as): # TODO: Fix "label"
        # Mark xyz coordinate
        # Return new xyz coord value(s)
        mark_coord_message = {
            **RPC_REQUEST,
            "body": [{
                "kind": "update_resource",
                "args": {
                    "resource": {
                        "kind": "identifier",
                        "args": {
                            "label": "test_location" # What is happening here??
                        }
                    }
                },
                "body": [{
                    "kind": "pair",
                    "args": {
                        "label": property,
                        "value": mark_as
                    }
                }]
            }]
        }

    # TODO: verify_tool() --> get broker message example
        # Verify tool exists at xyz coord
        # Return xyz coord and info(?)

    def mount_tool(self, tool_str):
        # Mount tool at xyz coord
        # No inherent return value
        lua_code = f"""
            mount_tool("{tool_str}")
        """

        self.lua(lua_code)

    def dismount_tool(self):
        # Dismount tool (at xyz coord?)
        # No inherent return value
        lua_code = """
            dismount_tool()
        """

        self.lua(lua_code)

    def water(self, point_id):
        # Dispense water at all or single xyz coords
        # No inherent return value
        plants = self.api.get_info("points", point_id)
        plant_name = plants["name"]

        lua_code = f"""
            water({plant_name})
        """

        self.lua(lua_code)

    def dispense(self, mL, tool_str, pin):
        # Dispense from source at all or single xyz coords
        # No inherent return value
        lua_code = f"""
            dispense({mL}, {{tool_name = "{tool_str}", pin = {pin}}})
        """

        self.lua(lua_code)

    def get_seed_tray_cell(self, tray, cell):
        lua_code = f"""
            tray = variable("Seed Tray")
            cell_label = variable("Seed Tray Cell")
            cell = get_seed_tray_cell({tray}, cell_label)
            cell_depth = 5

            local cell_coordinates = " (" .. cell.x .. ", " .. cell.y .. ", " .. cell.z - cell_depth .. ")"
            toast("Picking up seed from cell " .. cell_label .. cell_coordinates)

            move_absolute({{
                x = cell.x,
                y = cell.y,
                z = cell.z + 25,
                safe_z = true
            }})
        """

        self.lua(lua_code)

    def sequence(self, sequence_id):
        # Execute sequence by id
        # No inherent return value
        sequence_message = {
            **RPC_REQUEST,
            "body": [{
                "kind": "execute",
                "args": {
                    "sequence_id": sequence_id
                }
            }]
        }

        self.broker_connect.publish(sequence_message)

    # https://developer.farm.bot/v15/lua/functions/jobs.html

    def get_job(self, job_str):
        # Get all or single job by name
        status_data = self.read_status()

        if job_str is None:
            jobs = status_data["jobs"]
        else:
            jobs = status_data["jobs"][job_str]

        # Return job as json object: job[""]
        return jobs

    def set_job(self, job_str, status_message, value):
        lua_code = f"""
            local job_name = "{job_str}"
            set_job(job_name)

            -- Update the job's status and percent:
            set_job(job_name, {{
            status = "{status_message}",
            percent = {value}
            }})
        """

        self.lua(lua_code)

    def complete_job(self, job_str):
        lua_code = f"""
            complete_job("{job_str}")
        """

        self.lua(lua_code)

    def lua(self, code_snippet):
        # Send custom code snippet
        # No inherent return value
        lua_message = {
            **RPC_REQUEST,
            "body": [{
                "kind": "lua",
                "args": {
                    "lua": code_snippet
                }
            }]
        }

        self.broker_connect.publish(lua_message)

    def if_statement(self, variable, operator, value, then_id, else_id): # TODO: add 'do nothing' functionality
        # Execute if statement
        # No inherent return value
        if_statement_message = {
            **RPC_REQUEST,
            "body": [{
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
            }]
        }

        self.broker_connect.publish(if_statement_message)

    def assertion(self, code, as_type, id=''): # TODO: add 'continue' functionality
        # Execute assertion
        # No inherent return value
        assertion_message = {
            **RPC_REQUEST,
            "body": [{
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
            }]
        }

        self.broker_connect.publish(assertion_message)
