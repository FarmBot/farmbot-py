"""
Information class.
"""

# └── functions/information
#     ├── [API] api_get()
#     ├── [API] api_patch()
#     ├── [API] api_post()
#     ├── [API] api_delete()
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

    def api_get(self, endpoint, database_id=None):
        """Get information about a specific endpoint."""
        self.state.print_status(description=f"Retrieving {endpoint} information.")

        endpoint_data = self.api.request("GET", endpoint, database_id)

        self.state.print_status(update_only=True, endpoint_json=endpoint_data)

        return endpoint_data

    def api_patch(self, endpoint, new_data, database_id=None):
        """Change information contained within an endpoint."""
        self.state.print_status(description=f"Editing {endpoint}.")

        result = self.api.request("PATCH", endpoint, database_id=database_id, payload=new_data)

        self.state.print_status(update_only=True, endpoint_json=result)

        return result

    def api_post(self, endpoint, new_data):
        """Create new information contained within an endpoint."""
        self.state.print_status(description=f"Adding new data to {endpoint}.")

        result = self.api.request("POST", endpoint, database_id=None, payload=new_data)

        self.state.print_status(update_only=True, endpoint_json=result)

        return result

    def api_delete(self, endpoint, database_id=None):
        """Delete information contained within an endpoint."""
        self.state.print_status(description=f"Deleting {endpoint} with id={database_id}.")

        result = self.api.request("DELETE", endpoint, database_id=database_id)

        self.state.print_status(update_only=True, endpoint_json=result)

        return result

    def safe_z(self):
        """Returns the highest safe point along the z-axis."""

        config_data = self.api_get('fbos_config')
        z_value = config_data["safe_height"]

        self.state.print_status(description=f"Safe z={z_value}")
        return z_value

    def garden_size(self):
        """Return size of garden bed."""

        json_data = self.api_get('firmware_config')

        x_steps = json_data['movement_axis_nr_steps_x']
        x_mm = json_data['movement_step_per_mm_x']

        y_steps = json_data['movement_axis_nr_steps_y']
        y_mm = json_data['movement_step_per_mm_y']

        z_steps = json_data['movement_axis_nr_steps_z']
        z_mm = json_data['movement_step_per_mm_z']

        garden_size = {
            "x": x_steps / x_mm,
            "y": y_steps / y_mm,
            "z": z_steps / z_mm,
        }

        self.state.print_status(endpoint_json=garden_size)
        return garden_size

    def group(self, group_id=None):
        """Returns all group info or single by id."""

        if group_id is None:
            group_data = self.api_get("point_groups")
        else:
            group_data = self.api_get('point_groups', group_id)

        self.state.print_status(endpoint_json=group_data)
        return group_data

    def curve(self, curve_id=None):
        """Returns all curve info or single by id."""

        if curve_id is None:
            curve_data = self.api_get("curves")
        else:
            curve_data = self.api_get('curves', curve_id)

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

        status_tree = self.state.last_messages.get("status")

        self.state.print_status(update_only=True, endpoint_json=status_tree)
        return status_tree

    def read_sensor(self, sensor_name):
        """Reads the given pin by id."""
        self.state.print_status(description="Reading sensor...")
        sensor = self.get_resource_by_name("sensors", sensor_name)
        if sensor is None:
            return
        sensor_id = sensor["id"]
        mode = sensor["mode"]

        sensor_message = {
            "kind": "read_pin",
            "args": {
                "pin_mode": mode,
                "label": "---",
                "pin_number": {
                    "kind": "named_pin",
                    "args": {
                        "pin_type": "Sensor",
                        "pin_id": sensor_id,
                    }
                }
            }
        }

        self.broker.publish(sensor_message)

    def get_resource_by_name(self, endpoint, resource_name, name_key="label"):
        """Find a resource by name."""
        self.state.print_status(description=f"Searching for {resource_name} in {endpoint}.")
        resources = self.api_get(endpoint)
        resource_names = [resource[name_key] for resource in resources]
        if resource_name not in resource_names:
            error = f"ERROR: '{resource_name}' not in {endpoint}: {resource_names}."
            self.state.print_status(description=error, update_only=True)
            self.state.error = error
            return None

        resource = [p for p in resources if p[name_key] == resource_name][0]
        return resource
