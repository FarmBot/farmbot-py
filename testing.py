import unittest
import json
from unittest.mock import Mock, patch

from main import Farmbot

class TestFarmbot(unittest.TestCase):
    """Farmbot tests"""

    @patch('requests.post')
    def test_get_token_default_server(self, mock_post):
        """POSITIVE TEST: function called with email, password, and default server"""
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

    @patch('requests.post')
    def test_get_token_custom_server(self, mock_post):
        """POSITIVE TEST: function called with email, password, and custom server"""
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

    @patch('requests.post')
    def test_get_token_bad_email(self, mock_post):
        """NEGATIVE TEST: function called with incorrect email"""
        mock_response = Mock()
        error_response = {'error': 'bad email or password'}
        mock_response.json.return_value = error_response
        mock_response.status_code = 422
        mock_post.return_value = mock_response
        fb = Farmbot()
        with self.assertRaises(Exception):
            fb.get_token('bad_email@gmail.com', 'test_pass_123')
        mock_post.assert_called_once_with(
            'https://my.farm.bot/api/tokens',
            headers={'content-type': 'application/json'},
            json={'user': {'email': 'bad_email@gmail.com', 'password': 'test_pass_123'}}
        )
        self.assertEqual(mock_post.return_value.status_code, 422)

    @patch('requests.post')
    def test_get_token_bad_server(self, mock_post):
        """NEGATIVE TEST: function called with incorrect server"""
        mock_response = Mock()
        error_response = {'error': 'bad server'}
        mock_response.json.return_value = error_response
        mock_response.status_code = 404
        mock_post.return_value = mock_response
        fb = Farmbot()
        with self.assertRaises(Exception):
            fb.get_token('test_email@gmail.com', 'test_pass_123', 'https://bad.farm.bot')
        mock_post.assert_called_once_with(
            'https://bad.farm.bot/api/tokens',
            headers={'content-type': 'application/json'},
            json={'user': {'email': 'test_email@gmail.com', 'password': 'test_pass_123'}}
        )
        self.assertEqual(mock_post.return_value.status_code, 404)

    @patch('requests.get')
    def test_get_info_with_id(self, mock_get):
        """POSITIVE TEST: function called with valid ID"""
        mock_response = Mock()
        expected_info = {'id': '12345', 'info': 'farmbot_info'}
        mock_response.json.return_value = expected_info
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        fb = Farmbot()
        info = fb.get_info('12345')
        mock_get.assert_called_once_with(
            'https://my.farm.bot/api/resources/12345',
            headers = {'authorization': self.token['token']['encoded'], 'content-type': 'application/json'}
        )
        self.assertEqual(info, expected_info)
        self.assertEqual(mock_get.return_value.status_code, 200)

if __name__ == '__main__':
    unittest.main()