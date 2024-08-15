"""
Farmbot class unit tests.
"""

import json
import unittest
from unittest.mock import Mock, patch, call

from main import Farmbot

MOCK_TOKEN = {
    'token': {
        'unencoded': {
            'iss': '//my.farm.bot',
            'mqtt': 'mqtt_url',
            'bot': 'device_0',
        },
        'encoded': 'encoded_token_value'
    }
}

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
            json={'user': {'email': 'test_email@gmail.com',
                           'password': 'test_pass_123'}}
        )
        self.assertEqual(fb.token, expected_token)

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
        fb.get_token('test_email@gmail.com', 'test_pass_123',
                     'https://staging.farm.bot')
        mock_post.assert_called_once_with(
            'https://staging.farm.bot/api/tokens',
            headers={'content-type': 'application/json'},
            json={'user': {'email': 'test_email@gmail.com',
                           'password': 'test_pass_123'}}
        )
        self.assertEqual(fb.token, expected_token)

    @patch('requests.post')
    def test_get_token_bad_email(self, mock_post):
        """NEGATIVE TEST: function called with incorrect email"""
        mock_response = Mock()
        mock_response.status_code = 422
        mock_post.return_value = mock_response
        fb = Farmbot()
        # Call with bad email
        fb.get_token('bad_email@gmail.com', 'test_pass_123')
        mock_post.assert_called_once_with(
            'https://my.farm.bot/api/tokens',
            headers={'content-type': 'application/json'},
            json={'user': {'email': 'bad_email@gmail.com',
                           'password': 'test_pass_123'}}
        )
        self.assertEqual(
            fb.error, 'HTTP ERROR: Incorrect email address or password.')
        self.assertIsNone(fb.token)

    @patch('requests.post')
    def test_get_token_bad_server(self, mock_post):
        """NEGATIVE TEST: function called with incorrect server"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_post.return_value = mock_response
        fb = Farmbot()
        # Call with bad server
        fb.get_token('test_email@gmail.com',
                     'test_pass_123', 'https://bad.farm.bot')
        mock_post.assert_called_once_with(
            'https://bad.farm.bot/api/tokens',
            headers={'content-type': 'application/json'},
            json={'user': {'email': 'test_email@gmail.com',
                           'password': 'test_pass_123'}}
        )
        self.assertEqual(
            fb.error, 'HTTP ERROR: The server address does not exist.')
        self.assertIsNone(fb.token)

    @patch('requests.request')
    def test_get_info_endpoint_only(self, mock_request):
        """POSITIVE TEST: function called with endpoint only"""
        mock_response = Mock()
        expected_response = {'device': 'info'}
        mock_response.json.return_value = expected_response
        mock_response.status_code = 200
        mock_request.return_value = mock_response
        fb = Farmbot()
        fb.set_token(MOCK_TOKEN)
        # Call with endpoint only
        response = fb.get_info('device')
        mock_request.assert_called_once_with(
            'GET',
            'https://my.farm.bot/api/device',
            headers={
                'authorization': 'encoded_token_value',
                'content-type': 'application/json'
            },
            json=None,
        )
        self.assertEqual(response, expected_response)

    @patch('requests.request')
    def test_get_info_with_id(self, mock_request):
        """POSITIVE TEST: function called with valid ID"""
        mock_response = Mock()
        expected_response = {'peripheral': 'info'}
        mock_response.json.return_value = expected_response
        mock_response.status_code = 200
        mock_request.return_value = mock_response
        fb = Farmbot()
        fb.set_token(MOCK_TOKEN)
        # Call with specific ID
        response = fb.get_info('peripherals', '12345')
        mock_request.assert_called_once_with(
            'GET',
            'https://my.farm.bot/api/peripherals/12345',
            headers={
                'authorization': 'encoded_token_value',
                'content-type': 'application/json',
            },
            json=None,
        )
        self.assertEqual(response, expected_response)

    @patch('requests.request')
    def test_set_info(self, mock_request):
        """test set_info function"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'name': 'new name'}
        mock_request.return_value = mock_response
        fb = Farmbot()
        fb.set_token(MOCK_TOKEN)
        device_info = fb.set_info('device', 'name', 'new name')
        mock_request.assert_has_calls([call(
            'PATCH',
            'https://my.farm.bot/api/device',
            headers={
                'authorization': 'encoded_token_value',
                'content-type': 'application/json',
            },
            json={'name': 'new name'},
        ),
            call().json(),
            call(
            'GET',
            'https://my.farm.bot/api/device',
            headers={
                'authorization': 'encoded_token_value',
                'content-type': 'application/json',
            },
            json=None,
        ),
            call().json(),
        ])
        self.assertEqual(device_info, {'name': 'new name'})

    @patch('requests.request')
    def test_group(self, mock_request):
        """test group function"""
        mock_response = Mock()
        mock_response.json.return_value = {'name': 'Group 0'}
        mock_response.status_code = 200
        mock_request.return_value = mock_response
        fb = Farmbot()
        fb.set_token(MOCK_TOKEN)
        group_info = fb.group(12345)
        mock_request.assert_called_once_with(
            'GET',
            'https://my.farm.bot/api/point_groups/12345',
            headers={
                'authorization': 'encoded_token_value',
                'content-type': 'application/json',
            },
            json=None,
        )
        self.assertEqual(group_info, {'name': 'Group 0'})

    @patch('requests.request')
    def test_curve(self, mock_request):
        """test curve function"""
        mock_response = Mock()
        mock_response.json.return_value = {'name': 'Curve 0'}
        mock_response.status_code = 200
        mock_request.return_value = mock_response
        fb = Farmbot()
        fb.set_token(MOCK_TOKEN)
        curve_info = fb.curve(12345)
        mock_request.assert_called_once_with(
            'GET',
            'https://my.farm.bot/api/curves/12345',
            headers={
                'authorization': 'encoded_token_value',
                'content-type': 'application/json',
            },
            json=None,
        )
        self.assertEqual(curve_info, {'name': 'Curve 0'})

    @patch('requests.request')
    def test_safe_z(self, mock_request):
        """test safe_z function"""
        mock_response = Mock()
        mock_response.json.return_value = {'safe_height': 100}
        mock_response.status_code = 200
        mock_request.return_value = mock_response
        fb = Farmbot()
        fb.set_token(MOCK_TOKEN)
        safe_height = fb.safe_z()
        mock_request.assert_called_once_with(
            'GET',
            'https://my.farm.bot/api/fbos_config',
            headers={
                'authorization': 'encoded_token_value',
                'content-type': 'application/json',
            },
            json=None,
        )
        self.assertEqual(safe_height, 100)

    @patch('requests.request')
    def test_garden_size(self, mock_request):
        """test garden_size function"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'movement_axis_nr_steps_x': 1000,
            'movement_axis_nr_steps_y': 2000,
            'movement_step_per_mm_x': 5,
            'movement_step_per_mm_y': 5,
        }
        mock_response.status_code = 200
        mock_request.return_value = mock_response
        fb = Farmbot()
        fb.set_token(MOCK_TOKEN)
        garden_size = fb.garden_size()
        mock_request.assert_called_once_with(
            'GET',
            'https://my.farm.bot/api/firmware_config',
            headers={
                'authorization': 'encoded_token_value',
                'content-type': 'application/json',
            },
            json=None,
        )
        self.assertEqual(garden_size, (200, 400, 80000))

    @patch('requests.request')
    def test_log(self, mock_request):
        """test log function"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_request.return_value = mock_response
        fb = Farmbot()
        fb.set_token(MOCK_TOKEN)
        fb.log('test message', 'info', ['toast'])
        mock_request.assert_called_once_with(
            'POST',
            'https://my.farm.bot/api/logs',
            headers={
                'authorization': 'encoded_token_value',
                'content-type': 'application/json',
            },
            json={
                'message': 'test message',
                'type': 'info',
                'channel': ['toast'],
            },
        )

    @patch('paho.mqtt.client.Client')
    def test_connect_broker(self, mock_mqtt):
        '''Test test_connect_broker command'''
        mock_client = Mock()
        mock_mqtt.return_value = mock_client
        fb = Farmbot()
        fb.set_token(MOCK_TOKEN)
        fb.connect_broker()
        mock_client.username_pw_set.assert_called_once_with(
            username='device_0',
            password='encoded_token_value')
        mock_client.connect.assert_called_once_with(
            'mqtt_url',
            port=1883,
            keepalive=60)
        mock_client.loop_start.assert_called()

    def test_disconnect_broker(self):
        '''Test disconnect_broker command'''
        mock_client = Mock()
        fb = Farmbot()
        fb.broker.client = mock_client
        fb.disconnect_broker()
        mock_client.loop_stop.assert_called_once()
        mock_client.disconnect.assert_called_once()

    @patch('paho.mqtt.client.Client')
    def test_listen_broker(self, mock_mqtt):
        '''Test listen_broker command'''
        mock_client = Mock()
        mock_mqtt.return_value = mock_client
        fb = Farmbot()
        fb.set_token(MOCK_TOKEN)
        fb.listen_broker(1)
        mock_client.on_connect('', '', '', '')

        class MockMessage:
            '''Mock message class'''
            topic = 'topic'
            payload = '{"message": "test message"}'
        mock_client.on_message('', '', MockMessage())
        mock_client.username_pw_set.assert_called_once_with(
            username='device_0',
            password='encoded_token_value')
        mock_client.connect.assert_called_once_with(
            'mqtt_url',
            port=1883,
            keepalive=60)
        mock_client.subscribe.assert_called_once_with('bot/device_0/#')
        mock_client.loop_start.assert_called()
        mock_client.loop_stop.assert_called_once()
        mock_client.disconnect.assert_called_once()

    @patch('requests.request')
    @patch('paho.mqtt.client.Client')
    def send_command_test_helper(self, *args, **kwargs):
        '''Helper for testing command execution'''
        execute_command = args[0]
        mock_mqtt = args[1]
        mock_request = args[2]
        expected_command = kwargs.get('expected_command')
        extra_rpc_args = kwargs.get('extra_rpc_args')
        mock_api_response = kwargs.get('mock_api_response')
        mock_client = Mock()
        mock_mqtt.return_value = mock_client
        mock_response = Mock()
        mock_response.json.return_value = mock_api_response
        mock_response.status_code = 200
        mock_request.return_value = mock_response
        fb = Farmbot()
        fb.set_token(MOCK_TOKEN)
        execute_command(fb)
        expected_payload = {
            'kind': 'rpc_request',
            'args': {'label': '', **extra_rpc_args},
            'body': [expected_command],
        }
        mock_client.username_pw_set.assert_called_once_with(
            username='device_0',
            password='encoded_token_value')
        mock_client.connect.assert_called_once_with(
            'mqtt_url',
            port=1883,
            keepalive=60)
        mock_client.loop_start.assert_called()
        mock_client.publish.assert_called_once_with(
            'bot/device_0/from_clients',
            payload=json.dumps(expected_payload))

    def test_message(self):
        '''Test message command'''
        def exec_command(fb):
            fb.message('test message', 'info')
        self.send_command_test_helper(
            exec_command,
            expected_command={
                'kind': 'send_message',
                'args': {'message': 'test message', 'message_type': 'info'},
                'body': [{'kind': 'channel', 'args': {'channel_name': 'ticker'}}],
            },
            extra_rpc_args={'priority': 600},
            mock_api_response={})

    def test_debug(self):
        '''Test debug command'''
        def exec_command(fb):
            fb.debug('test message')
        self.send_command_test_helper(
            exec_command,
            expected_command={
                'kind': 'send_message',
                'args': {'message': 'test message', 'message_type': 'debug'},
                'body': [{'kind': 'channel', 'args': {'channel_name': 'ticker'}}],
            },
            extra_rpc_args={'priority': 600},
            mock_api_response={})

    def test_toast(self):
        '''Test toast command'''
        def exec_command(fb):
            fb.toast('test message')
        self.send_command_test_helper(
            exec_command,
            expected_command={
                'kind': 'send_message',
                'args': {'message': 'test message', 'message_type': 'info'},
                'body': [{'kind': 'channel', 'args': {'channel_name': 'toast'}}],
            },
            extra_rpc_args={'priority': 600},
            mock_api_response={})

    def test_read_status(self):
        '''Test read_status command'''
        def exec_command(fb):
            fb.read_status()
        self.send_command_test_helper(
            exec_command,
            expected_command={
                'kind': 'read_status',
                'args': {},
            },
            extra_rpc_args={'priority': 600},
            mock_api_response={})

    def test_read_sensor(self):
        '''Test read_sensor command'''
        def exec_command(fb):
            fb.read_sensor(123)
        self.send_command_test_helper(
            exec_command,
            expected_command={
                'kind': 'read_pin',
                'args': {
                    'pin_mode': 0,
                    'label': '---',
                    'pin_number': {
                        'kind': 'named_pin',
                        'args': {'pin_type': 'Peripheral', 'pin_id': 123},
                    },
                },
            },
            extra_rpc_args={},
            mock_api_response={'mode': 0})

    def test_assertion(self):
        '''Test assertion command'''
        def exec_command(fb):
            fb.assertion('return true', 'abort')
        self.send_command_test_helper(
            exec_command,
            expected_command={
                'kind': 'assertion',
                'args': {
                    'lua': 'return true',
                    '_then': {'kind': 'execute', 'args': {'sequence_id': ''}},
                    'assertion_type': 'abort'
                }
            },
            extra_rpc_args={},
            mock_api_response={})

    def test_wait(self):
        '''Test wait command'''
        def exec_command(fb):
            fb.wait(123)
        self.send_command_test_helper(
            exec_command,
            expected_command={
                'kind': 'wait',
                'args': {'milliseconds': 123},
            },
            extra_rpc_args={'priority': 600},
            mock_api_response={})

    def test_unlock(self):
        '''Test unlock command'''
        def exec_command(fb):
            fb.unlock()
        self.send_command_test_helper(
            exec_command,
            expected_command={
                'kind': 'emergency_unlock',
                'args': {},
            },
            extra_rpc_args={'priority': 9000},
            mock_api_response={})

    def test_e_stop(self):
        '''Test e_stop command'''
        def exec_command(fb):
            fb.e_stop()
        self.send_command_test_helper(
            exec_command,
            expected_command={
                'kind': 'emergency_lock',
                'args': {},
            },
            extra_rpc_args={'priority': 9000},
            mock_api_response={})

    def test_find_home(self):
        '''Test find_home command'''
        def exec_command(fb):
            fb.find_home()
        self.send_command_test_helper(
            exec_command,
            expected_command={
                'kind': 'find_home',
                'args': {'axis': 'all', 'speed': 100},
            },
            extra_rpc_args={'priority': 600},
            mock_api_response={})

    def test_set_home(self):
        '''Test set_home command'''
        def exec_command(fb):
            fb.set_home()
        self.send_command_test_helper(
            exec_command,
            expected_command={
                'kind': 'zero',
                'args': {'axis': 'all'},
            },
            extra_rpc_args={'priority': 600},
            mock_api_response={})

    def test_toggle_peripheral(self):
        '''Test toggle_peripheral command'''
        def exec_command(fb):
            fb.toggle_peripheral(123)
        self.send_command_test_helper(
            exec_command,
            expected_command={
                'kind': 'toggle_pin',
                'args': {
                    'pin_number': {
                        'kind': 'named_pin',
                        'args': {'pin_type': 'Peripheral', 'pin_id': 123},
                    },
                },
            },
            extra_rpc_args={},
            mock_api_response={})

    def test_on(self):
        '''Test on command'''
        def exec_command(fb):
            fb.on(123)
        self.send_command_test_helper(
            exec_command,
            expected_command={
                'kind': 'write_pin',
                'args': {
                    'pin_value': 1,
                    'pin_mode': 0,
                    'pin_number': {
                        'kind': 'named_pin',
                        'args': {'pin_type': 'Peripheral', 'pin_id': 123},
                    },
                },
            },
            extra_rpc_args={},
            mock_api_response={'mode': 0})

    def test_off(self):
        '''Test off command'''
        def exec_command(fb):
            fb.off(123)
        self.send_command_test_helper(
            exec_command,
            expected_command={
                'kind': 'write_pin',
                'args': {
                    'pin_value': 0,
                    'pin_mode': 1,
                    'pin_number': {
                        'kind': 'named_pin',
                        'args': {'pin_type': 'Peripheral', 'pin_id': 123},
                    },
                },
            },
            extra_rpc_args={},
            mock_api_response={'mode': 1})

    def test_move(self):
        '''Test move command'''
        def exec_command(fb):
            fb.move(1, 2, 3)
        self.send_command_test_helper(
            exec_command,
            expected_command={
                'kind': 'move',
                'args': {},
                'body': [
                    {'kind': 'axis_overwrite', 'args': {
                        'axis': 'x',
                        'axis_operand': {'kind': 'numeric', 'args': {'number': 1}}}},
                    {'kind': 'axis_overwrite', 'args': {
                        'axis': 'y',
                        'axis_operand': {'kind': 'numeric', 'args': {'number': 2}}}},
                    {'kind': 'axis_overwrite', 'args': {
                        'axis': 'z',
                        'axis_operand': {'kind': 'numeric', 'args': {'number': 3}}}},
                ],
            },
            extra_rpc_args={'priority': 600},
            mock_api_response={})

    def test_reboot(self):
        '''Test reboot command'''
        def exec_command(fb):
            fb.reboot()
        self.send_command_test_helper(
            exec_command,
            expected_command={
                'kind': 'reboot',
                'args': {'package': 'farmbot_os'},
            },
            extra_rpc_args={},
            mock_api_response={})

    def test_shutdown(self):
        '''Test shutdown command'''
        def exec_command(fb):
            fb.shutdown()
        self.send_command_test_helper(
            exec_command,
            expected_command={
                'kind': 'power_off',
                'args': {},
            },
            extra_rpc_args={},
            mock_api_response={})

    def test_axis_length(self):
        '''Test axis_length command'''
        def exec_command(fb):
            fb.axis_length()
        self.send_command_test_helper(
            exec_command,
            expected_command={
                'kind': 'calibrate',
                'args': {'axis': 'all'},
            },
            extra_rpc_args={},
            mock_api_response={})

    def test_control_peripheral(self):
        '''Test control_peripheral command'''
        def exec_command(fb):
            fb.control_peripheral(123, 456, 0)
        self.send_command_test_helper(
            exec_command,
            expected_command={
                'kind': 'write_pin',
                'args': {
                    'pin_value': 456,
                    'pin_mode': 0,
                    'pin_number': {
                        'kind': 'named_pin',
                        'args': {'pin_type': 'Peripheral', 'pin_id': 123},
                    },
                },
            },
            extra_rpc_args={},
            mock_api_response={'mode': 0})

    def test_soil_height(self):
        '''Test soil_height command'''
        def exec_command(fb):
            fb.soil_height()
        self.send_command_test_helper(
            exec_command,
            expected_command={
                'kind': 'execute_script',
                'args': {'label': 'Measure Soil Height'},
            },
            extra_rpc_args={},
            mock_api_response={})

    def test_detect_weeds(self):
        '''Test detect_weeds command'''
        def exec_command(fb):
            fb.detect_weeds()
        self.send_command_test_helper(
            exec_command,
            expected_command={
                'kind': 'execute_script',
                'args': {'label': 'plant-detection'},
            },
            extra_rpc_args={},
            mock_api_response={})

    def test_calibrate_camera(self):
        '''Test calibrate_camera command'''
        def exec_command(fb):
            fb.calibrate_camera()
        self.send_command_test_helper(
            exec_command,
            expected_command={
                'kind': 'execute_script',
                'args': {'label': 'camera-calibration'},
            },
            extra_rpc_args={},
            mock_api_response={})

    def test_sequence(self):
        '''Test sequence command'''
        def exec_command(fb):
            fb.sequence(123)
        self.send_command_test_helper(
            exec_command,
            expected_command={
                'kind': 'execute',
                'args': {'sequence_id': 123},
            },
            extra_rpc_args={},
            mock_api_response={})

    def test_take_photo(self):
        '''Test take_photo command'''
        def exec_command(fb):
            fb.take_photo()
        self.send_command_test_helper(
            exec_command,
            expected_command={
                'kind': 'take_photo',
                'args': {},
            },
            extra_rpc_args={},
            mock_api_response={})

    def test_control_servo(self):
        '''Test control_servo command'''
        def exec_command(fb):
            fb.control_servo(4, 100)
        self.send_command_test_helper(
            exec_command,
            expected_command={
                'kind': 'set_servo_angle',
                'args': {
                    'pin_number': 4,
                    'pin_value': 100,
                },
            },
            extra_rpc_args={},
            mock_api_response={'mode': 0})

    def test_get_xyz(self):
        '''Test get_xyz command'''
        def exec_command(fb):
            fb.broker.last_message = {
                'location_data': {'position': {'x': 1, 'y': 2, 'z': 3}},
            }
            position = fb.get_xyz()
            self.assertEqual(position, (1, 2, 3))
        self.send_command_test_helper(
            exec_command,
            expected_command={
                'kind': 'read_status',
                'args': {},
            },
            extra_rpc_args={'priority': 600},
            mock_api_response={})

    def test_check_position(self):
        '''Test check_position command: at position'''
        def exec_command(fb):
            fb.broker.last_message = {
                'location_data': {'position': {'x': 1, 'y': 2, 'z': 3}},
            }
            at_position = fb.check_position(1, 2, 3, 0)
            self.assertTrue(at_position)
        self.send_command_test_helper(
            exec_command,
            expected_command={
                'kind': 'read_status',
                'args': {},
            },
            extra_rpc_args={'priority': 600},
            mock_api_response={})

    def test_check_position_false(self):
        '''Test check_position command: not at position'''
        def exec_command(fb):
            fb.broker.last_message = {
                'location_data': {'position': {'x': 1, 'y': 2, 'z': 3}},
            }
            at_position = fb.check_position(0, 0, 0, 2)
            self.assertFalse(at_position)
        self.send_command_test_helper(
            exec_command,
            expected_command={
                'kind': 'read_status',
                'args': {},
            },
            extra_rpc_args={'priority': 600},
            mock_api_response={})

    def test_mount_tool(self):
        '''Test mount_tool command'''
        def exec_command(fb):
            fb.mount_tool('Weeder')
        self.send_command_test_helper(
            exec_command,
            expected_command={
                'kind': 'lua',
                'args': {'lua': 'mount_tool("Weeder")'},
            },
            extra_rpc_args={},
            mock_api_response={})

    def test_dismount_tool(self):
        '''Test dismount_tool command'''
        def exec_command(fb):
            fb.dismount_tool()
        self.send_command_test_helper(
            exec_command,
            expected_command={
                'kind': 'lua',
                'args': {'lua': 'dismount_tool()'},
            },
            extra_rpc_args={},
            mock_api_response={})

    def test_water(self):
        '''Test water command'''
        def exec_command(fb):
            fb.water(123)
        self.send_command_test_helper(
            exec_command,
            expected_command={
                'kind': 'lua',
                'args': {'lua': """plant = api({
                method = "GET",
                url = "/api/points/123"
            })
            water(plant)"""},
            },
            extra_rpc_args={},
            mock_api_response={'name': 'Mint'})

    def test_dispense(self):
        '''Test dispense command'''
        def exec_command(fb):
            fb.dispense(100, 'Weeder', 4)
        self.send_command_test_helper(
            exec_command,
            expected_command={
                'kind': 'lua',
                'args': {
                    'lua': 'dispense(100, {tool_name = "Weeder", pin = 4})',
                },
            },
            extra_rpc_args={},
            mock_api_response={})

    @patch('paho.mqtt.client.Client')  # temporary
    @patch('requests.request')
    def test_get_seed_tray_cell(self, mock_request, _mock_client):
        '''Test get_seed_tray_cell command'''
        mock_response = Mock()
        mock_api_response = {
            'pointer_type': 'ToolSlot',
            'pullout_direction': 1,
            'x': 0,
            'y': 0,
            'z': 0,
        }
        mock_response.json.return_value = mock_api_response
        mock_response.status_code = 200
        mock_request.return_value = mock_response
        fb = Farmbot()
        fb.set_token(MOCK_TOKEN)
        cell = fb.get_seed_tray_cell(123, 'd4')
        mock_request.assert_called_once_with(
            'GET',
            'https://my.farm.bot/api/points/123',
            headers={
                'authorization': 'encoded_token_value',
                'content-type': 'application/json',
            },
            json=None,
        )
        self.assertEqual(cell, {'x': -36.25, 'y': 18.75, 'z': 0})

    def test_get_job(self):
        '''Test get_job command'''
        def exec_command(fb):
            fb.broker.last_message = {
                'jobs': {
                    'job name': {'status': 'working'},
                },
            }
            job = fb.get_job('job name')
            self.assertEqual(job, {'status': 'working'})
        self.send_command_test_helper(
            exec_command,
            expected_command={
                'kind': 'read_status',
                'args': {},
            },
            extra_rpc_args={'priority': 600},
            mock_api_response={})

    def test_set_job(self):
        '''Test set_job command'''
        def exec_command(fb):
            fb.set_job('job name', 'working', 50)
        self.send_command_test_helper(
            exec_command,
            expected_command={
                'kind': 'lua',
                'args': {'lua': """local job_name = "job name"
            set_job(job_name)

            -- Update the job's status and percent:
            set_job(job_name, {
            status = "working",
            percent = 50
            })"""},
            },
            extra_rpc_args={},
            mock_api_response={})

    def test_complete_job(self):
        '''Test complete_job command'''
        def exec_command(fb):
            fb.complete_job('job name')
        self.send_command_test_helper(
            exec_command,
            expected_command={
                'kind': 'lua',
                'args': {'lua': 'complete_job("job name")'},
            },
            extra_rpc_args={},
            mock_api_response={})

    def test_lua(self):
        '''Test lua command'''
        def exec_command(fb):
            fb.lua('return true')
        self.send_command_test_helper(
            exec_command,
            expected_command={
                'kind': 'lua',
                'args': {'lua': 'return true'},
            },
            extra_rpc_args={},
            mock_api_response={})

    def test_if_statement(self):
        '''Test if_statement command'''
        def exec_command(fb):
            fb.if_statement('pin10', '<', 0, 123, 456)
        self.send_command_test_helper(
            exec_command,
            expected_command={
                'kind': '_if',
                'args': {
                    'lhs': 'pin10',
                    'op': '<',
                    'rhs': 0,
                    '_then': {'kind': 'execute', 'args': {'sequence_id': 123}},
                    '_else': {'kind': 'execute', 'args': {'sequence_id': 456}},
                }
            },
            extra_rpc_args={},
            mock_api_response={})


if __name__ == '__main__':
    unittest.main()
