import unittest
import json
from funct_CLASSES import Farmbot
from unittest.mock import patch, Mock

class TestFarmbot(unittest.TestCase):

    ## POSITIVE TEST: function called with email, password, and default server
    @patch('requests.post')
    def test_get_token_default_server(self, mock_post):
        mock_response = Mock()
        expected_token = {'token': 'abc123'}
        mock_response.json.return_value = expected_token
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        fb = Farmbot()

        # Call with default server
        fb.get_token('test_email@gmail.com', 'test_pass_123')

        mock_post.assert_called_once_with(
            'https://my.farm.bot/api/tokens',
            headers={'content-type': 'application/json'},
            json={'user': {'email': 'test_email@gmail.com', 'password': 'test_pass_123'}}
        )

        self.assertEqual(fb.token, expected_token)
        self.assertEqual(mock_post.return_value.status_code, 200)

    # POSITIVE TEST: function called with email, password, and custom server
    @patch('requests.post')
    def test_get_token_custom_server(self, mock_post):
        mock_response = Mock()
        expected_token = {'token': 'abc123'}
        mock_response.json.return_value = expected_token
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        fb = Farmbot()

        # Call with custom server
        fb.get_token('test_email@gmail.com', 'test_pass_123', 'https://staging.farm.bot')

        mock_post.assert_called_once_with(
            'https://staging.farm.bot/api/tokens',
            headers={'content-type': 'application/json'},
            json={'user': {'email': 'test_email@gmail.com', 'password': 'test_pass_123'}}
        )

        self.assertEqual(fb.token, expected_token)
        self.assertEqual(mock_post.return_value.status_code, 200)

    # NEGATIVE TEST: function called with bad email or password (HTTP error)
    @patch('requests.post')
    def test_get_token_bad_email(self, mock_post):
        mock_response = Mock()
        mock_response.status_code = 422
        mock_post.return_value = mock_response

        fb = Farmbot()

        # Call with bad email
        fb.get_token('bad_email@gmail.com', 'test_pass_123', 'https://staging.farm.bot')

        mock_post.assert_called_once_with(
            'https://staging.farm.bot/api/tokens',
            headers={'content-type': 'application/json'},
            json={'user': {'email': 'bad_email@gmail.com', 'password': 'test_pass_123'}}
        )

        self.assertIsNone(fb.token)
        self.assertEqual(mock_post.return_value.status_code, 422)

    # NEGATIVE TEST: function called with bad server address (HTTP error)
    @patch('requests.post')
    def test_get_token_bad_email(self, mock_post):
        mock_response = Mock()
        mock_response.status_code = 404
        mock_post.return_value = mock_response

        fb = Farmbot()

        # Call with bad email
        fb.get_token('test_email@gmail.com', 'test_pass_123', 'https://bad.farm.bot')

        mock_post.assert_called_once_with(
            'https://bad.farm.bot/api/tokens',
            headers={'content-type': 'application/json'},
            json={'user': {'email': 'test_email@gmail.com', 'password': 'test_pass_123'}}
        )

        self.assertIsNone(fb.token)
        self.assertEqual(mock_post.return_value.status_code, 404)

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

if __name__ == '__main__':
    unittest.main()