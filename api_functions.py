from api_connect import ApiConnect

class ApiFunctions():
    def __init__(self):
        self.api_connect = ApiConnect()
        self.token = None

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

    def get_token(self, email, password, server='https://my.farm.bot'):
        token_str = self.api_connect.get_token(email, password, server)
        return token_str

    # data = get_info() and like functions will assign 'data' JSON object
    # data["name"] will access the field "name" and return the field value

    def get_info(self, endpoint, id=None):
        return self.api_connect.get(endpoint, id)

    def set_info(self, endpoint, field, value, id=None):
        new_value = {
            field: value
        }

        self.api_connect.patch(endpoint, id, new_value)
        return self.api_connect.get(endpoint, id)

    def env(self, id=None, field=None, new_val=None): # TODO: why are there '?'
        if id is None:
            data = self.api_connect.get('farmware_envs', id=None)
            print(data) # ?
        else:
            data = self.api_connect.get('farmware_envs', id)
            print(data) # ?
        # return ...

    def log(self, message, type=None, channel=None):
        log_message = {
            "message": message,
            "type": type, # https://software.farm.bot/v15/app/intro/jobs-and-logs#log-types
            "channel": channel # Specifying channel does not do anything
        }

        endpoint = 'logs'
        id = None

        self.api_connect.post(endpoint, id, log_message)
        # return ...

    def safe_z(self):
        json_data = self.get_info('fbos_config')
        return json_data['safe_height']

    def garden_size(self):
        json_data = self.get_info('firmware_config')

        x_steps = json_data['movement_axis_nr_steps_x']
        x_mm = json_data['movement_step_per_mm_x']

        y_steps = json_data['movement_axis_nr_steps_y']
        y_mm = json_data['movement_step_per_mm_y']

        length_x = x_steps / x_mm
        length_y = y_steps / y_mm
        area = length_x * length_y

        return print(f'Garden size:\n'
                    f'\tx length = {length_x:.2f}\n'
                    f'\ty length = {length_y:.2f}\n'
                    f'\tarea = {area:.2f}')

    def group(self, id): # TODO: make ID optional return full tree w/o ID
        return self.get_info('point_groups', id)

    def curve(self, id): # TODO: make ID optional return full tree w/o ID
        return self.get_info('curves', id)
