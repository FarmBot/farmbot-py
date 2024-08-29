"""
Information class.
"""

# └── functions/information
#     ├── [API] get_info()
#     ├── [API] edit_info()
#     ├── [API] add_info()
#     ├── [API] delete_info()
#     ├── [API] safe_z()
#     ├── [API] garden_size()
#     ├── [API] group()
#     ├── [API] curve()
#     ├── [BROKER] measure_soil_height()
#     ├── [BROKER] read_status()
#     └── [BROKER] read_sensor()

from .broker import BrokerConnect
from .api import ApiConnect

class Information():
    """Information class."""
    def __init__(self, state):
        self.broker = BrokerConnect(state)
        self.api = ApiConnect(state)
        self.state = state

    def get_info(self, endpoint, database_id=None):
        """Get information about a specific endpoint."""
        self.state.print_status(description=f"Retrieving {endpoint} information.")

        endpoint_data = self.api.request("GET", endpoint, database_id)

        self.state.print_status(update_only=True, endpoint_json=endpoint_data)

        return endpoint_data

    def edit_info(self, endpoint, new_data, database_id=None):
        """Change information contained within an endpoint."""
        self.state.print_status(description=f"Editing {endpoint}.")

        result = self.api.request("PATCH", endpoint, database_id=database_id, payload=new_data)

        self.state.print_status(update_only=True, endpoint_json=result)

        return result

    def add_info(self, endpoint, new_data):
        """Create new information contained within an endpoint."""
        self.state.print_status(description=f"Adding new data to {endpoint}.")

        result = self.api.request("POST", endpoint, database_id=None, payload=new_data)

        self.state.print_status(update_only=True, endpoint_json=result)

        return result

    def delete_info(self, endpoint, database_id=None):
        """Delete information contained within an endpoint."""
        self.state.print_status(description=f"Deleting {endpoint} with id={database_id}.")

        result = self.api.request("DELETE", endpoint, database_id=database_id)

        self.state.print_status(update_only=True, endpoint_json=result)

        return result

    def safe_z(self):
        """Returns the highest safe point along the z-axis."""

        config_data = self.get_info('fbos_config')
        z_value = config_data["safe_height"]

        self.state.print_status(description=f"Safe z={z_value}")
        return z_value

    def garden_size(self):
        """Returns x-axis length, y-axis length, and area of garden bed."""

        json_data = self.get_info('firmware_config')

        x_steps = json_data['movement_axis_nr_steps_x']
        x_mm = json_data['movement_step_per_mm_x']

        y_steps = json_data['movement_axis_nr_steps_y']
        y_mm = json_data['movement_step_per_mm_y']

        length_x = x_steps / x_mm
        length_y = y_steps / y_mm
        area = length_x * length_y

        self.state.print_status(description=f"X-axis length={length_x}\n Y-axis length={length_y}\n Area={area}")
        return length_x, length_y, area

    def group(self, group_id=None):
        """Returns all group info or single by id."""

        if group_id is None:
            group_data = self.get_info("point_groups")
        else:
            group_data = self.get_info('point_groups', group_id)

        self.state.print_status(endpoint_json=group_data)
        return group_data

    def curve(self, curve_id=None):
        """Returns all curve info or single by id."""

        if curve_id is None:
            curve_data = self.get_info("curves")
        else:
            curve_data = self.get_info('curves', curve_id)

        self.state.print_status(endpoint_json=curve_data)
        return curve_data

    def measure_soil_height(self):
        """Use the camera to measure the soil height at the current location."""

        measure_soil_height_message = {
            "kind": "execute_script",
            "args": {
                "label": "Measure Soil Height"
            }
        }

        self.broker.publish(measure_soil_height_message)

    def read_status(self):
        """Returns the FarmBot status tree."""
        self.state.print_status(description="Reading status...")
        status_message = {
            "kind": "read_status",
            "args": {}
        }
        self.broker.publish(status_message)

        self.broker.listen(self.state.broker_listen_duration, "status")

        status_tree = self.state.last_message

        self.state.print_status(update_only=True, endpoint_json=status_tree)
        return status_tree

    def read_sensor(self, peripheral_id):
        """Reads the given pin by id."""

        peripheral_str = self.get_info("peripherals", peripheral_id)
        mode = peripheral_str["mode"]

        sensor_message = {
            "kind": "read_pin",
            "args": {
                "pin_mode": mode,
                "label": "---",
                "pin_number": {
                    "kind": "named_pin",
                    "args": {
                        "pin_type": "Peripheral",
                        "pin_id": peripheral_id,
                    }
                }
            }
        }

        self.broker.publish(sensor_message)
