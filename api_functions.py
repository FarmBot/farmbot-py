from api_connect import ApiConnect

# main.py -> api_functions.py -> api_connect.py

class ApiFunctions():
    def __init__(self):
        self.connect = ApiConnect()

        self.token = None
        self.error = None

    def get_token(self, email, password, server='https://my.farm.bot'):
        # when get_token() is called, set self.token
        self.token = self.connect.get_token(email, password, server)

        # when get_token() is called, set api.token
        self.connect.token = self.token
        # when get_token() is called, set broker.token
        self.broker.token = self.token

        return self.token

    def get_info(self, endpoint, id=None):
        return self.connect.get(endpoint, id)
        # return self.connect.get(endpoint, id)...

    def set_info(self, endpoint, field, value, id=None):
        new_value = {
            field: value
        }

        self.connect.patch(endpoint, id, new_value)
        return self.connect.get(endpoint, id)
        # return self.connect.get(endpoint, id)...

    def env(self, id=None, field=None, new_val=None):
        if id is None:
            data = self.connect.get('farmware_envs', id=None)
            print(data)
        else:
            data = self.connect.get('farmware_envs', id)
            print(data)

    def log(self, message, type=None, channel=None):
        log_message = {
            "message": message,
            "type": type,
            "channel": channel # Specifying channel does not do anything
        }

        endpoint = 'logs'
        id = None

        self.connect.post(endpoint, id, log_message)
        # return ...

    def safe_z(self):
        json_data = self.get_info('fbos_config')
        return json_data['safe_height']
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
        return size_value

    def group(self, id):
        return self.get_info('point_groups', id)
        # return self.get_info('point_groups', id)...

    def curve(self, id):
        return self.get_info('curves', id)
        # return self.get_info('curves', id)...
