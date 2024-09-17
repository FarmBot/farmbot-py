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
#     ├── [API] curve()
#     ├── [BROKER] measure_soil_height()
#     ├── [BROKER] read_status()
#     ├── [BROKER] read_pin()
#     └── [BROKER] read_sensor()

from .broker import BrokerConnect
from .api import ApiConnect


class Information():
    """Information class."""

    def __init__(self, state):
        self.broker = BrokerConnect(state)
        self.api = ApiConnect(state)
        self.state = state

    def api_get(self, endpoint, database_id=None, payload=None, data_print=True):
        """Get information about a specific endpoint."""
        self.state.print_status(
            description=f"Retrieving {endpoint} information.")

        endpoint_data = self.api.request(
            method="GET",
            endpoint=endpoint,
            database_id=database_id,
            payload=payload)

        if data_print:
            self.state.print_status(
                update_only=True,
                endpoint_json=endpoint_data)
        else:
            self.state.print_status(
                update_only=True,
                description=f"Fetched {len(endpoint_data)} items.")

        return endpoint_data

    def api_patch(self, endpoint, payload, database_id=None):
        """Change information contained within an endpoint."""
        self.state.print_status(description=f"Editing {endpoint}.")

        result = self.api.request(
            method="PATCH",
            endpoint=endpoint,
            database_id=database_id,
            payload=payload)

        self.state.print_status(update_only=True, endpoint_json=result)

        return result

    def api_post(self, endpoint, payload=None):
        """Create new information contained within an endpoint."""
        self.state.print_status(description=f"Adding new data to {endpoint}.")

        result = self.api.request(
            method="POST",
            endpoint=endpoint,
            database_id=None,
            payload=payload)

        self.state.print_status(update_only=True, endpoint_json=result)

        return result

    def api_delete(self, endpoint, database_id=None, payload=None):
        """Delete information contained within an endpoint."""
        self.state.print_status(
            description=f"Deleting {endpoint} with id={database_id}.")

        result = self.api.request(
            method="DELETE",
            endpoint=endpoint,
            database_id=database_id,
            payload=payload)

        self.state.print_status(update_only=True, endpoint_json=result)

        return result

    def safe_z(self):
        """Returns the highest safe point along the z-axis."""
        self.state.print_status(description="Retrieving safe z value...")

        config_data = self.api_get('fbos_config')
        z_value = config_data["safe_height"]

        self.state.print_status(
            description=f"Safe z={z_value}", update_only=True)
        return z_value

    def garden_size(self):
        """Return size of garden bed."""
        self.state.print_status(description="Retrieving garden size...")

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

        self.state.print_status(endpoint_json=garden_size, update_only=True)
        return garden_size

    def get_curve(self, curve_id):
        """Retrieve curve data from the API and return a curve object with extras."""
        self.state.print_status(description="Preparing curve information...")

        api_curve_data = self.api_get("curves", curve_id)
        if isinstance(api_curve_data, str):
            return None
        return Curve(api_curve_data)

    def measure_soil_height(self):
        """Use the camera to measure the soil height at the current location."""
        self.state.print_status(description="Measuring soil height...")

        measure_soil_height_message = {
            "kind": "execute_script",
            "args": {
                "label": "Measure Soil Height"
            }
        }

        self.broker.publish(measure_soil_height_message)

    def read_status(self, path=None):
        """Returns the FarmBot status tree."""
        path_str = "" if path is None else f" of {path}"
        self.state.print_status(description=f"Reading status{path_str}...")
        status_message = {
            "kind": "read_status",
            "args": {}
        }
        self.broker.publish(status_message)

        status_trees = self.state.last_messages.get("status", [])
        status_tree = None
        if len(status_trees) > 0:
            status_tree = status_trees[-1]["content"]

        if path is not None:
            for key in path.split("."):
                status_tree = status_tree[key]

        self.state.print_status(update_only=True, endpoint_json=status_tree)
        return status_tree

    @staticmethod
    def convert_mode_to_number(mode):
        """Converts mode string to mode number."""
        modes = ["digital", "analog"]
        if str(mode).lower() not in modes:
            raise ValueError(f"Invalid mode: {mode} not in {modes}")
        return 0 if mode.lower() == "digital" else 1

    def read_pin(self, pin_number, mode="digital"):
        """Reads the given pin by number."""
        pin_mode = self.convert_mode_to_number(mode)
        self.state.print_status(
            description=f"Reading pin {pin_number} ({mode})...")
        read_pin_message = {
            "kind": "read_pin",
            "args": {
                "pin_number": pin_number,
                "label": "---",
                "pin_mode": pin_mode,
            }
        }
        self.broker.publish(read_pin_message)

    def read_sensor(self, sensor_name):
        """Reads the given sensor."""
        self.state.print_status(description=f"Reading {sensor_name} sensor...")
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

    def get_resource_by_name(self, endpoint, resource_name, name_key="label", query=None):
        """Find a resource by name."""
        self.state.print_status(
            description=f"Searching for {resource_name} in {endpoint}.")
        resources = self.state.fetch_cache(endpoint)
        if resources is None:
            resources = self.api_get(endpoint, data_print=False)
        else:
            self.state.print_status(
                description=f"Using {len(resources)} cached items.")
        if query is not None:
            for key, value in query.items():
                resources = [res for res in resources if res[key] == value]
        names = [resource[name_key] for resource in resources]
        if resource_name not in names:
            error = f"ERROR: '{resource_name}' not in {endpoint}: {names}."
            self.state.print_status(description=error, update_only=True)
            self.state.error = error
            self.state.clear_cache(endpoint)
            return None

        self.state.save_cache(endpoint, resources)
        resource = [p for p in resources if p[name_key] == resource_name][0]
        return resource


class Curve:
    """Curve data object for the get_curve() function to return."""

    def __init__(self, curve_data):
        self.curve_data = curve_data
        self.name = curve_data["name"]
        self.type = curve_data["type"]
        self.unit = "mL" if self.type == "water" else "mm"

    def __getitem__(self, key):
        """Allow dictionary-style access to attributes."""
        return getattr(self, key)

    def day(self, day):
        """Calculate the value for a specific day based on the curve data."""
        day = int(day)
        data = self.curve_data["data"]
        data = {int(key): val for key, val in data.items()}
        value = data.get(day)
        if value is not None:
            return value

        sorted_day_keys = sorted(data.keys())
        prev_day = None
        next_day = None
        for day_key in sorted_day_keys:
            if day_key < day:
                prev_day = day_key
            elif day_key > day and next_day is None:
                next_day = day_key
                break

        if prev_day is None:
            return data[sorted_day_keys[0]]

        if next_day is None:
            return data[sorted_day_keys[-1]]

        exact_value = (data[prev_day] * (next_day - day) +
                       data[next_day] * (day - prev_day)
                       ) / (next_day - prev_day)
        return round(exact_value, 2)
