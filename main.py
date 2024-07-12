from api_functions import ApiFunctions
from broker_functions import BrokerFunctions

class Farmbot():
    def __init__(self):
        self.api = ApiFunctions()
        self.broker = BrokerFunctions()

        self.token = None

    def get_token(self, email, password, server="https://my.farm.bot"):
        token_data = self.api.get_token(email, password, server)

        self.token = token_data

        self.api.token = token_data
        self.api.api_connect.token = token_data

        self.broker.token = token_data
        self.broker.broker_connect = token_data

        return token_data

    def get_info(self, endpoint, id=None):
        return self.api.get_info(endpoint, id)

    def connect(self):
        self.broker.broker_connect.connect()
        return print("Connected to message broker.")
