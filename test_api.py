import unittest
from unittest.mock import patch, MagicMock
from farmbot_util_PORT import Farmbot

class TestFarmbot(unittest.TestCase):

    def setUp(self):
        self.farmbot = Farmbot()

    @patch('farmbot_util_PORT.FarmbotAPI.get_token')
    def test_get_token(self, mock_get_token):
        mock_get_token.return_value = 'fake_token'
        self.farmbot.get_token('test@example.com', 'password123')
        self.assertEqual(self.farmbot.token, 'fake_token')
        mock_get_token.assert_called_once_with('test@example.com', 'password123', 'https://my.farm.bot')

    @patch('farmbot_util_PORT.FarmbotAPI.get_info')
    def test_get_info(self, mock_get_info):
        mock_get_info.return_value = {'info': 'fake_info'}
        result = self.farmbot.get_info()
        self.assertEqual(result, {'info': 'fake_info'})
        mock_get_info.assert_called_once()

    @patch('farmbot_util_PORT.FarmbotAPI.set_info')
    def test_set_info(self, mock_set_info):
        self.farmbot.set_info('label', 'value')
        mock_set_info.assert_called_once_with('label', 'value')

    @patch('farmbot_util_PORT.FarmbotAPI.log')
    def test_log(self, mock_log):
        self.farmbot.log('message', 'info')
        mock_log.assert_called_once_with('message', 'info')

    @patch('farmbot_util_PORT.FarmbotAPI.safe_z')
    def test_safe_z(self, mock_safe_z):
        mock_safe_z.return_value = 10
        result = self.farmbot.safe_z()
        self.assertEqual(result, 10)
        mock_safe_z.assert_called_once()

    @patch('farmbot_util_PORT.FarmbotAPI.garden_size')
    def test_garden_size(self, mock_garden_size):
        mock_garden_size.return_value = {'x': 1000, 'y': 2000}
        result = self.farmbot.garden_size()
        self.assertEqual(result, {'x': 1000, 'y': 2000})
        mock_garden_size.assert_called_once()

    @patch('farmbot_util_PORT.FarmbotAPI.group')
    def test_group(self, mock_group):
        sequences = ['seq1', 'seq2']
        mock_group.return_value = {'grouped': True}
        result = self.farmbot.group(sequences)
        self.assertEqual(result, {'grouped': True})
        mock_group.assert_called_once_with(sequences)

    @patch('farmbot_util_PORT.FarmbotAPI.curve')
    def test_curve(self, mock_curve):
        mock_curve.return_value = {'curve': True}
        result = self.farmbot.curve('seq', 0, 0, 10, 10, 5, 5)
        self.assertEqual(result, {'curve': True})
        mock_curve.assert_called_once_with('seq', 0, 0, 10, 10, 5, 5)

if __name__ == '__main__':
    unittest.main()
