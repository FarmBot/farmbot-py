import unittest
from unittest.mock import MagicMock, patch

from main import Farmbot
from api_functions import ApiFunctions
from broker_functions import BrokerFunctions

class TestApiFunctions(unittest.TestCase):

    @patch('main.ApiFunctions')
    def setUp(self, MockApiFunctions):
        self.mock_api = MockApiFunctions.return_value
        self.farmbot = Farmbot()

    def test_get_token(self):
        self.mock_api.get_token.return_value = 'mock_token'

        email = 'test@example.com'
        password = 'password'
        server = 'https://my.farm.bot'

        token = self.farmbot.get_token(email, password, server)

        self.assertEqual(token, 'mock_token')
        self.assertEqual(self.farmbot.token, 'mock_token')
        self.assertEqual(self.farmbot.api.token, 'mock_token')
        self.assertEqual(self.farmbot.api.api_connect.token, 'mock_token')

        self.mock_api.get_token.assert_called_with(email, password, server)

    def test_get_info(self):
        self.mock_api.get_info.return_value = 'info_data'

        endpoint = 'endpoint'
        id = 123

        data = self.farmbot.get_info(endpoint, id)

        self.assertEqual(data, 'info_data')
        self.mock_api.get_info.assert_called_with(endpoint, id)

if __name__ == '__main__':
    unittest.main()
