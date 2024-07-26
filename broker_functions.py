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

class BrokerFunctions():
    def __init__(self):
        self.broker_connect = BrokerConnect()
        self.api = ApiFunctions()

        self.client = None

    def read_status(self):
        # Get device status tree
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

        # Return status as json object: status[""]
        return status_tree

    def read_sensor(self, id):
        # Get sensor data
        # Return sensor as json object: sensor[""]
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

    def message(self, message, type=None, channel=None):
        # Send new log message via broker
        # No inherent return value
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

    def debug(self, message):
        # Send 'debug' type message
        # No inherent return value
        self.message(message, 'debug')

    def toast(self, message):
        # Send 'toast' type message
        # No inherent return value
        self.message(message, 'toast')

    def wait(self, duration):
        # Tell bot to wait for some time
        # No inherent return value
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
        # Tell bot to emergency stop
        # No inherent return value
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
        # Tell bot to unlock
        # No inherent return value
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
        # Tell bot to reboot
        # No inherent return value
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
        # Tell bot to shutdown
        # No inherent return value
        shutdown_message = {
            **RPC_REQUEST,
            "body": {
                "kind": "power_off",
                "args": {}
            }
        }

        self.broker_connect.publish(shutdown_message)
        return print("Triggered device shutdown.")

    def move(self, x, y, z):
        # Tell bot to move to new xyz coord
        # Return new xyz position as values
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

    def set_home(self, axis='all'):
        # Set current xyz coord as 0,0,0
        # No inherent return value
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

    def find_home(self, axis='all', speed=100):
        # Move to 0,0,0
        # Return new xyz position as values
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

    def axis_length(self, axis='all'):
        # Get axis length
        # Return axis length as values
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
        # Order group of points with method
        # Return ???

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
        # Execute soil height scripts
        # Return soil height as value
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

    def detect_weeds(self):
        # Execute detect weeds script
        # Return array of weeds with xyz coords
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

    def calibrate_camera(self): # TODO: fix "sequence_id"
        # Execute calibrate camera script
        # No inherent return value
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

    def photo_grid(self): # TODO: fix "sequence_id"
        # Execute photo grid script
        # No inherent return value
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

    def take_photo(self):
        # Take single photo
        # No inherent return value
        take_photo_message = {
            **RPC_REQUEST,
            "body": {
                "kind": "take_photo",
                "args": {}
            }
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
                "body": {
                    "kind": "set_servo_angle",
                    "args": {
                        "pin_number": pin,
                        "pin_value": angle # From 0 to 180
                    }
                }
            }

            self.broker_connect.publish(control_servo_message)

    def mark_coord(self, x, y, z, property, mark_as): # TODO: Fix "label"
        # Mark xyz coordinate
        # Return new xyz coord value(s)
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

    # TODO: verify_tool() --> get broker message example
        # Verify tool exists at xyz coord
        # Return xyz coord and info(?)
    # TODO: mount_tool() --> get broker message example
        # Mount tool at xyz coord
        # No inherent return value
    # TODO: dismount_tool() --> get broker message example
        # Dismount tool (at xyz coord?)
        # No inherent return value

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

    # TODO: water() --> all or single coords
        # Dispense water at all or single xyz coords
        # No inherent return value
    # TODO: dispense() --> single coords?
        # Dispense from source at all or single xyz coords
        # No inherent return value

    # TODO: get_seed_tray_call(tray, cell) --> get coordinates of cell in seed tray by passing tool object and cell id, eg B3
        # Get xyz coords of cell in seed tray
        # Return xyz coords (as ??)

    def sequence(self, sequence_id):
        # Execute sequence by id
        # No inherent return value
        sequence_message = {
            **RPC_REQUEST,
            "body": {
                "kind": "execute",
                "args": {
                    "sequence_id": sequence_id
                }
            }
        }

        self.broker_connect.publish(sequence_message)

    # https://developer.farm.bot/v15/lua/functions/jobs.html

    def get_job(self, job_str=None):
        # Get all or single job by name
        status_data = self.read_status()

        if job_str is None:
            jobs = status_data["jobs"]
        else:
            jobs = status_data["jobs"][job_str]

        # Return job as json object: job[""]
        return jobs

    def set_job(self, job_str, field=None, new_val=None):
        # Add new or edit single by name
        status_data = self.read_status()
        jobs = status_data["jobs"]

        good_jobs = json.dumps(jobs, indent=4)
        print(good_jobs)

        # Check existing jobs to see if job_str exists
        # If job_str does not exist, append new job to end of jobs list
        if job_str not in jobs:
            jobs[job_str] = {
                "status": "Working", # Initialize 'status' to 'Working'
                "type": "unknown",
                "unit": "percent",
                "time": datetime.now().isoformat(), # Initialize 'time' to current time
                "updated_at": "null",
                "file_type": "null",
                'percent': 0 # Initialize 'percent' to '0'
            }

        self.broker_connect.publish(jobs)

        # Update field of job_str with new_val
        # if field and new_val:
        #     jobs[job_str][field].update(new_val)

        # Return job as json object: job[""]
        return None

    def complete_job(self, job_str):
        status_data = self.read_status()
        jobs = status_data["jobs"]

        # Set job status as 'complete' updated at current time
        set_complete = {
            "status": "Complete",
            "updated_at": datetime.now().isoformat()
        }

        # Return job as json object: job[""]

    def lua(self, code_snippet): # TODO: verify working
        # Send custom code snippet
        # No inherent return value
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

    def if_statement(self, variable, operator, value, then_id, else_id): # TODO: add 'do nothing' functionality
        # Execute if statement
        # No inherent return value
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

    def assertion(self, code, as_type, id=''): # TODO: add 'continue' functionality
        # Execute assertion
        # No inherent return value
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
