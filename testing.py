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

    # POSITIVE TEST: function called with endpoint only
    @patch('requests.get')
    def test_get_info_endpoint_only(self, mock_get):
        mock_token = {
            'token': {
                'unencoded': {'iss': '//my.farm.bot'},
                'encoded': 'encoded_token_value'
            }
        }
        mock_response = Mock()
        expected_response = {'device': 'info'}
        mock_response.json.return_value = expected_response
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        fb = Farmbot()
        fb.token = mock_token

        # Call with endpoint only
        response = fb.get_info('device')

        mock_get.assert_called_once_with(
            'https://my.farm.bot/api/device/',
            headers={
                'authorization': 'encoded_token_value',
                'content-type': 'application/json'
            }
        )

        self.assertEqual(response, json.dumps(expected_response, indent=2))
        self.assertEqual(mock_get.return_value.status_code, 200)

    # POSITIVE TEST: function called with endpoint and ID value
    @patch('requests.get')
    def test_get_info_with_id(self, mock_get):
        mock_token = {
            'token': {
                'unencoded': {'iss': '//my.farm.bot'},
                'encoded': 'encoded_token_value'
            }
        }
        mock_response = Mock()
        expected_response = {'peripheral': 'info'}
        mock_response.json.return_value = expected_response
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        fb = Farmbot()
        fb.token = mock_token

        # Call with specific ID
        response = fb.get_info('peripherals', '12345')

        mock_get.assert_called_once_with(
            'https://my.farm.bot/api/peripherals/12345',
            headers={
                'authorization': 'encoded_token_value',
                'content-type': 'application/json'
            }
        )

        self.assertEqual(response, json.dumps(expected_response, indent=2))
        self.assertEqual(mock_get.return_value.status_code, 200)

# class TestFarmbot_api(unittest.TestCase):

#     def setUp(self):
#         self.farmbot = Farmbot()

#     @patch('farmbot_util_PORT.FarmbotAPI.get_token')
#     def test_get_token(self, mock_get_token):
#         mock_get_token.return_value = 'fake_token'
#         self.farmbot.get_token('test@example.com', 'password123')
#         self.assertEqual(self.farmbot.token, 'fake_token')
#         mock_get_token.assert_called_once_with('test@example.com', 'password123', 'https://my.farm.bot')

#     @patch('farmbot_util_PORT.FarmbotAPI.get_info')
#     def test_get_info(self, mock_get_info):
#         mock_get_info.return_value = {'info': 'fake_info'}
#         result = self.farmbot.get_info()
#         self.assertEqual(result, {'info': 'fake_info'})
#         mock_get_info.assert_called_once()

#     @patch('farmbot_util_PORT.FarmbotAPI.set_info')
#     def test_set_info(self, mock_set_info):
#         self.farmbot.set_info('label', 'value')
#         mock_set_info.assert_called_once_with('label', 'value')

#     @patch('farmbot_util_PORT.FarmbotAPI.log')
#     def test_log(self, mock_log):
#         self.farmbot.log('message', 'info')
#         mock_log.assert_called_once_with('message', 'info')

#     @patch('farmbot_util_PORT.FarmbotAPI.safe_z')
#     def test_safe_z(self, mock_safe_z):
#         mock_safe_z.return_value = 10
#         result = self.farmbot.safe_z()
#         self.assertEqual(result, 10)
#         mock_safe_z.assert_called_once()

#     @patch('farmbot_util_PORT.FarmbotAPI.garden_size')
#     def test_garden_size(self, mock_garden_size):
#         mock_garden_size.return_value = {'x': 1000, 'y': 2000}
#         result = self.farmbot.garden_size()
#         self.assertEqual(result, {'x': 1000, 'y': 2000})
#         mock_garden_size.assert_called_once()

#     @patch('farmbot_util_PORT.FarmbotAPI.group')
#     def test_group(self, mock_group):
#         sequences = ['seq1', 'seq2']
#         mock_group.return_value = {'grouped': True}
#         result = self.farmbot.group(sequences)
#         self.assertEqual(result, {'grouped': True})
#         mock_group.assert_called_once_with(sequences)

#     @patch('farmbot_util_PORT.FarmbotAPI.curve')
#     def test_curve(self, mock_curve):
#         mock_curve.return_value = {'curve': True}
#         result = self.farmbot.curve('seq', 0, 0, 10, 10, 5, 5)
#         self.assertEqual(result, {'curve': True})
#         mock_curve.assert_called_once_with('seq', 0, 0, 10, 10, 5, 5)

if __name__ == '__main__':
    unittest.main()
