import json

from api_connect import ApiConnect

class ApiFunctions():
    def __init__(self):
        self.api_connect = ApiConnect()

        self.echo = True
        self.verbose = True

    def get_token(self, email, password, server='https://my.farm.bot'):
        # Generate user authentication token
        token_str = self.api_connect.get_token(email, password, server)
        # Return token as json object: token[""]
        return token_str

    def get_info(self, endpoint, id=None):
        # Get endpoint info
        endpoint_data = self.api_connect.request('GET', endpoint, id)
        # Return endpoint info as json object: endpoint[""]
        return endpoint_data

    def set_info(self, endpoint, field, value, id=None):
        # Edit endpoint info
        new_value = {
            field: value
        }
        self.api_connect.request('PATCH', endpoint, id, new_value)

        # Return endpoint info as json object: endpoint[""]
        new_endpoint_data = self.api_connect.request('GET', endpoint, id)
        return new_endpoint_data

    def log(self, message, type=None, channel=None):
        # Send new log message via API
        log_message = {
            "message": message,
            "type": type, # https://software.farm.bot/v15/app/intro/jobs-and-logs#log-types
            "channel": channel # Specifying channel does not do anything
        }

        endpoint = 'logs'
        id = None

        self.api_connect.request('POST', endpoint, id, log_message)

        # No inherent return value

    def safe_z(self):
        # Get safe z height via get_info()
        config_data = self.get_info('fbos_config')
        z_value = config_data["safe_height"]
        # Return safe z height as value
        return z_value

    def garden_size(self):
        # Get garden size parameters via get_info()
        json_data = self.get_info('firmware_config')

        x_steps = json_data['movement_axis_nr_steps_x']
        x_mm = json_data['movement_step_per_mm_x']

        y_steps = json_data['movement_axis_nr_steps_y']
        y_mm = json_data['movement_step_per_mm_y']

        length_x = x_steps / x_mm
        length_y = y_steps / y_mm
        area = length_x * length_y

        # Return garden size parameters as values
        return length_x, length_y, area

    def group(self, id=None):
        # Get all groups or single by id
        if id is None:
            group_data = self.get_info("point_groups")
        else:
            group_data = self.get_info('point_groups', id)

        # Return group as json object: group[""]
        return group_data

    def curve(self, id=None):
        # Get all curves or single by id
        if id is None:
            curve_data = self.get_info("curves")
        else:
            curve_data = self.get_info('curves', id)

        # Return curve as json object: curve[""]
        return curve_data
