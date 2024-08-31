'''
Farmbot class unit tests.
'''

import json
import unittest
from unittest.mock import Mock, patch, call
import requests

from farmbot_sidecar_starter_pack import Farmbot

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
    '''Farmbot tests'''

    def setUp(self):
        '''Set up method called before each test case'''
        self.fb = Farmbot()
        self.fb.set_token(MOCK_TOKEN)
        self.fb.set_verbosity(0)
        self.fb.state.test_env = True
        self.fb.state.broker_listen_duration = 0

    @patch('requests.post')
    def test_get_token_default_server(self, mock_post):
        '''POSITIVE TEST: function called with email, password, and default server'''
        mock_response = Mock()
        expected_token = {'token': 'abc123'}
        mock_response.json.return_value = expected_token
        mock_response.status_code = 200
        mock_response.text = 'text'
        mock_post.return_value = mock_response
        self.fb.set_token(None)
        # Call with default server
        self.fb.get_token('test_email@gmail.com', 'test_pass_123')
        mock_post.assert_called_once_with(
            'https://my.farm.bot/api/tokens',
            headers={'content-type': 'application/json'},
            json={'user': {'email': 'test_email@gmail.com',
                           'password': 'test_pass_123'}}
        )
        self.assertEqual(self.fb.state.token, expected_token)

    @patch('requests.post')
    def test_get_token_custom_server(self, mock_post):
        '''POSITIVE TEST: function called with email, password, and custom server'''
        mock_response = Mock()
        expected_token = {'token': 'abc123'}
        mock_response.json.return_value = expected_token
        mock_response.status_code = 200
        mock_response.text = 'text'
        mock_post.return_value = mock_response
        self.fb.set_token(None)
        # Call with custom server
        self.fb.get_token('test_email@gmail.com', 'test_pass_123',
                          'https://staging.farm.bot')
        mock_post.assert_called_once_with(
            'https://staging.farm.bot/api/tokens',
            headers={'content-type': 'application/json'},
            json={'user': {'email': 'test_email@gmail.com',
                           'password': 'test_pass_123'}}
        )
        self.assertEqual(self.fb.state.token, expected_token)

    @patch('requests.post')
    def helper_get_token_errors(self, *args, **kwargs):
        '''Test helper for get_token errors'''
        mock_post = args[0]
        status_code = kwargs['status_code']
        error_msg = kwargs['error_msg']
        mock_response = Mock()
        mock_response.status_code = status_code
        mock_post.return_value = mock_response
        self.fb.set_token(None)
        self.fb.get_token('email@gmail.com', 'test_pass_123')
        mock_post.assert_called_once_with(
            'https://my.farm.bot/api/tokens',
            headers={'content-type': 'application/json'},
            json={'user': {'email': 'email@gmail.com',
                           'password': 'test_pass_123'}}
        )
        self.assertEqual(self.fb.state.error, error_msg)
        self.assertIsNone(self.fb.state.token)

    def test_get_token_bad_email(self):
        '''NEGATIVE TEST: function called with incorrect email'''
        self.helper_get_token_errors(
            status_code=422,
            error_msg='HTTP ERROR: Incorrect email address or password.',
        )

    def test_get_token_bad_server(self):
        '''NEGATIVE TEST: function called with incorrect server'''
        self.helper_get_token_errors(
            status_code=404,
            error_msg='HTTP ERROR: The server address does not exist.',
        )

    def test_get_token_other_error(self):
        '''get_token: other error'''
        self.helper_get_token_errors(
            status_code=500,
            error_msg='HTTP ERROR: Unexpected status code 500',
        )

    @patch('requests.post')
    def helper_get_token_exceptions(self, *args, **kwargs):
        '''Test helper for get_token exceptions'''
        mock_post = args[0]
        exception = kwargs['exception']
        error_msg = kwargs['error_msg']
        mock_post.side_effect = exception
        self.fb.set_token(None)
        self.fb.get_token('email@gmail.com', 'test_pass_123')
        mock_post.assert_called_once_with(
            'https://my.farm.bot/api/tokens',
            headers={'content-type': 'application/json'},
            json={'user': {'email': 'email@gmail.com',
                           'password': 'test_pass_123'}}
        )
        self.assertEqual(self.fb.state.error, error_msg)
        self.assertIsNone(self.fb.state.token)

    def test_get_token_server_not_found(self):
        '''get_token: server not found'''
        self.helper_get_token_exceptions(
            exception=requests.exceptions.ConnectionError,
            error_msg='DNS ERROR: The server address does not exist.',
        )

    def test_get_token_timeout(self):
        '''get_token: timeout'''
        self.helper_get_token_exceptions(
            exception=requests.exceptions.Timeout,
            error_msg='DNS ERROR: The request timed out.',
        )

    def test_get_token_problem(self):
        '''get_token: problem'''
        self.helper_get_token_exceptions(
            exception=requests.exceptions.RequestException,
            error_msg='DNS ERROR: There was a problem with the request.',
        )

    def test_get_token_other_exception(self):
        '''get_token: other exception'''
        self.helper_get_token_exceptions(
            exception=Exception('other'),
            error_msg='DNS ERROR: An unexpected error occurred: other',
        )

    @patch('requests.request')
    def helper_api_get_error(self, *args, **kwargs):
        '''Test helper for api_get errors'''
        mock_request = args[0]
        status_code = kwargs['status_code']
        error_msg = kwargs['error_msg']
        mock_response = Mock()
        mock_response.status_code = status_code
        mock_response.reason = 'reason'
        mock_response.text = 'text'
        mock_response.json.return_value = {'error': 'error'}
        mock_request.return_value = mock_response
        response = self.fb.api_get('device')
        mock_request.assert_called_once_with(
            'GET',
            'https://my.farm.bot/api/device',
            headers={
                'authorization': 'encoded_token_value',
                'content-type': 'application/json'
            },
            json=None,
        )
        self.assertEqual(response, error_msg)

    def test_api_get_errors(self):
        '''Test api_get errors'''
        self.helper_api_get_error(
            status_code=404,
            error_msg='CLIENT ERROR 404: The specified endpoint does not exist. ({\n  "error": "error"\n})',
        )
        self.helper_api_get_error(
            status_code=500,
            error_msg='SERVER ERROR 500: text ({\n  "error": "error"\n})',
        )
        self.helper_api_get_error(
            status_code=600,
            error_msg='UNEXPECTED ERROR 600: text ({\n  "error": "error"\n})',
        )

    @patch('requests.request')
    def test_api_string_error_response_handling(self, mock_request):
        '''Test API string response errors'''
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.reason = 'reason'
        mock_response.text = 'error string'
        mock_response.json.side_effect = requests.exceptions.JSONDecodeError('', '', 0)
        mock_request.return_value = mock_response
        response = self.fb.api_get('device')
        mock_request.assert_called_once_with(
            'GET',
            'https://my.farm.bot/api/device',
            headers={
                'authorization': 'encoded_token_value',
                'content-type': 'application/json'
            },
            json=None,
        )
        self.assertEqual(response, 'CLIENT ERROR 404: The specified endpoint does not exist. (error string)')

    @patch('requests.request')
    def test_api_string_error_response_handling_html(self, mock_request):
        '''Test API html string response errors'''
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.reason = 'reason'
        mock_response.text = '<html><h1>error0</h1><h2>error1</h2></html>'
        mock_response.json.side_effect = requests.exceptions.JSONDecodeError('', '', 0)
        mock_request.return_value = mock_response
        response = self.fb.api_get('device')
        mock_request.assert_called_once_with(
            'GET',
            'https://my.farm.bot/api/device',
            headers={
                'authorization': 'encoded_token_value',
                'content-type': 'application/json'
            },
            json=None,
        )
        self.assertEqual(response, 'CLIENT ERROR 404: The specified endpoint does not exist. (error0 error1)')

    @patch('requests.request')
    def test_api_get_endpoint_only(self, mock_request):
        '''POSITIVE TEST: function called with endpoint only'''
        mock_response = Mock()
        expected_response = {'device': 'info'}
        mock_response.json.return_value = expected_response
        mock_response.status_code = 200
        mock_response.text = 'text'
        mock_request.return_value = mock_response
        # Call with endpoint only
        response = self.fb.api_get('device')
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
    def test_api_get_with_id(self, mock_request):
        '''POSITIVE TEST: function called with valid ID'''
        mock_response = Mock()
        expected_response = {'peripheral': 'info'}
        mock_response.json.return_value = expected_response
        mock_response.status_code = 200
        mock_response.text = 'text'
        mock_request.return_value = mock_response
        # Call with specific ID
        response = self.fb.api_get('peripherals', '12345')
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
    def test_check_token_api_request(self, mock_request):
        '''Test check_token: API request'''
        self.fb.set_token(None)
        with self.assertRaises(ValueError) as cm:
            self.fb.api_get('points')
        self.assertEqual(cm.exception.args[0], self.fb.state.NO_TOKEN_ERROR)
        mock_request.assert_not_called()
        self.assertEqual(self.fb.state.error, self.fb.state.NO_TOKEN_ERROR)

    @patch('paho.mqtt.client.Client')
    @patch('requests.request')
    def test_check_token_broker(self, mock_request, mock_mqtt):
        '''Test check_token: broker'''
        mock_client = Mock()
        mock_mqtt.return_value = mock_client
        self.fb.set_token(None)
        with self.assertRaises(ValueError) as cm:
            self.fb.on(123)
        self.assertEqual(cm.exception.args[0], self.fb.state.NO_TOKEN_ERROR)
        with self.assertRaises(ValueError) as cm:
            self.fb.read_sensor(123)
        self.assertEqual(cm.exception.args[0], self.fb.state.NO_TOKEN_ERROR)
        with self.assertRaises(ValueError) as cm:
            self.fb.get_xyz()
        self.assertEqual(cm.exception.args[0], self.fb.state.NO_TOKEN_ERROR)
        with self.assertRaises(ValueError) as cm:
            self.fb.read_status()
        self.assertEqual(cm.exception.args[0], self.fb.state.NO_TOKEN_ERROR)
        mock_request.assert_not_called()
        mock_client.publish.assert_not_called()
        self.assertEqual(self.fb.state.error, self.fb.state.NO_TOKEN_ERROR)

    @patch('paho.mqtt.client.Client')
    def test_publish_disabled(self, mock_mqtt):
        '''Test publish disabled'''
        mock_client = Mock()
        mock_mqtt.return_value = mock_client
        self.fb.state.dry_run = True
        self.fb.on(123)
        mock_client.publish.assert_not_called()

    @patch('requests.request')
    def test_api_patch(self, mock_request):
        '''test api_patch function'''
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = 'text'
        mock_response.json.return_value = {'name': 'new name'}
        mock_request.return_value = mock_response
        device_info = self.fb.api_patch('device', {'name': 'new name'})
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
        ])
        self.assertEqual(device_info, {'name': 'new name'})

    @patch('requests.request')
    def test_api_post(self, mock_request):
        '''test api_post function'''
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = 'text'
        mock_response.json.return_value = {'name': 'new name'}
        mock_request.return_value = mock_response
        point = self.fb.api_post('points', {'name': 'new name'})
        mock_request.assert_has_calls([call(
            'POST',
            'https://my.farm.bot/api/points',
            headers={
                'authorization': 'encoded_token_value',
                'content-type': 'application/json',
            },
            json={'name': 'new name'},
        ),
            call().json(),
        ])
        self.assertEqual(point, {'name': 'new name'})

    @patch('requests.request')
    def test_api_delete(self, mock_request):
        '''test api_delete function'''
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = 'text'
        mock_response.json.return_value = {'name': 'deleted'}
        mock_request.return_value = mock_response
        result = self.fb.api_delete('points', 12345)
        mock_request.assert_called_once_with(
            'DELETE',
            'https://my.farm.bot/api/points/12345',
            headers={
                'authorization': 'encoded_token_value',
                'content-type': 'application/json',
            },
            json=None,
        )
        self.assertEqual(result, {'name': 'deleted'})

    @patch('requests.request')
    def test_api_delete_requests_disabled(self, mock_request):
        '''test api_delete function: requests disabled'''
        self.fb.state.dry_run = True
        result = self.fb.api_delete('points', 12345)
        mock_request.assert_not_called()
        self.assertEqual(result, {"edit_requests_disabled": True})

    @patch('requests.request')
    def test_group_one(self, mock_request):
        '''test group function: get one group'''
        mock_response = Mock()
        mock_response.json.return_value = {'name': 'Group 0'}
        mock_response.status_code = 200
        mock_response.text = 'text'
        mock_request.return_value = mock_response
        group_info = self.fb.group(12345)
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
    def test_group_all(self, mock_request):
        '''test group function: get all groups'''
        mock_response = Mock()
        mock_response.json.return_value = [{'name': 'Group 0'}]
        mock_response.status_code = 200
        mock_response.text = 'text'
        mock_request.return_value = mock_response
        group_info = self.fb.group()
        mock_request.assert_called_once_with(
            'GET',
            'https://my.farm.bot/api/point_groups',
            headers={
                'authorization': 'encoded_token_value',
                'content-type': 'application/json',
            },
            json=None,
        )
        self.assertEqual(group_info, [{'name': 'Group 0'}])

    @patch('requests.request')
    def test_curve_one(self, mock_request):
        '''test curve function: get one curve'''
        mock_response = Mock()
        mock_response.json.return_value = {'name': 'Curve 0'}
        mock_response.status_code = 200
        mock_response.text = 'text'
        mock_request.return_value = mock_response
        curve_info = self.fb.curve(12345)
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
    def test_curve_all(self, mock_request):
        '''test curve function: get all curves'''
        mock_response = Mock()
        mock_response.json.return_value = [{'name': 'Curve 0'}]
        mock_response.status_code = 200
        mock_response.text = 'text'
        mock_request.return_value = mock_response
        curve_info = self.fb.curve()
        mock_request.assert_called_once_with(
            'GET',
            'https://my.farm.bot/api/curves',
            headers={
                'authorization': 'encoded_token_value',
                'content-type': 'application/json',
            },
            json=None,
        )
        self.assertEqual(curve_info, [{'name': 'Curve 0'}])

    @patch('requests.request')
    def test_safe_z(self, mock_request):
        '''test safe_z function'''
        mock_response = Mock()
        mock_response.json.return_value = {'safe_height': 100}
        mock_response.status_code = 200
        mock_response.text = 'text'
        mock_request.return_value = mock_response
        safe_height = self.fb.safe_z()
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
        '''test garden_size function'''
        mock_response = Mock()
        mock_response.json.return_value = {
            'movement_axis_nr_steps_x': 1000,
            'movement_axis_nr_steps_y': 2000,
            'movement_axis_nr_steps_z': 40000,
            'movement_step_per_mm_x': 5,
            'movement_step_per_mm_y': 5,
            'movement_step_per_mm_z': 25,
        }
        mock_response.status_code = 200
        mock_response.text = 'text'
        mock_request.return_value = mock_response
        garden_size = self.fb.garden_size()
        mock_request.assert_called_once_with(
            'GET',
            'https://my.farm.bot/api/firmware_config',
            headers={
                'authorization': 'encoded_token_value',
                'content-type': 'application/json',
            },
            json=None,
        )
        self.assertEqual(garden_size, {'x': 200, 'y': 400, 'z': 1600})

    @patch('requests.request')
    def test_log(self, mock_request):
        '''test log function'''
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = 'text'
        mock_response.json.return_value = {'message': 'test message'}
        mock_request.return_value = mock_response
        self.fb.log('test message', 'info', 'toast')
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
                'channels': ['toast'],
            },
        )

    @patch('paho.mqtt.client.Client')
    def test_connect_broker(self, mock_mqtt):
        '''Test test_connect_broker command'''
        mock_client = Mock()
        mock_mqtt.return_value = mock_client
        self.fb.connect_broker()
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
        self.fb.broker.client = mock_client
        self.fb.disconnect_broker()
        mock_client.loop_stop.assert_called_once()
        mock_client.disconnect.assert_called_once()

    @patch('paho.mqtt.client.Client')
    def test_listen(self, mock_mqtt):
        '''Test listen command'''
        mock_client = Mock()
        mock_mqtt.return_value = mock_client
        self.fb.listen()

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
        mock_client.loop_stop.assert_called()

    @patch('paho.mqtt.client.Client')
    def test_listen_clear_last(self, mock_mqtt):
        '''Test listen command: clear last message'''
        mock_client = Mock()
        mock_mqtt.return_value = mock_client
        self.fb.state.last_messages = {'#': "message"}
        self.fb.state.test_env = False
        self.fb.listen()
        self.assertIsNone(self.fb.state.last_messages['#'])

    @patch('paho.mqtt.client.Client')
    def test_publish_apply_label(self, mock_mqtt):
        '''Test publish command: set uuid'''
        mock_client = Mock()
        mock_mqtt.return_value = mock_client
        self.fb.state.test_env = False
        self.fb.broker.publish({'kind': 'sync', 'args': {}})
        self.assertNotIn(self.fb.state.last_published.get('args', {}).get('label'), ['test', '', None])

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
        error = kwargs.get('error')
        mock_client = Mock()
        mock_mqtt.return_value = mock_client
        mock_response = Mock()
        mock_response.json.return_value = mock_api_response
        mock_response.status_code = 200
        mock_response.text = 'text'
        mock_request.return_value = mock_response
        self.fb.state.last_messages['from_device'] = {
            'kind': 'rpc_error' if error else 'rpc_ok',
            'args': {'label': 'test'},
        }
        execute_command()
        if expected_command is None:
            mock_client.publish.assert_not_called()
            return
        expected_payload = {
            'kind': 'rpc_request',
            'args': {'label': 'test', **extra_rpc_args},
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
        if not error:
            self.assertNotEqual(self.fb.state.error, 'RPC error response received.')

    def test_message(self):
        '''Test message command'''
        def exec_command():
            self.fb.message('test message', 'info')
        self.send_command_test_helper(
            exec_command,
            expected_command={
                'kind': 'send_message',
                'args': {'message': 'test message', 'message_type': 'info'},
                'body': [{'kind': 'channel', 'args': {'channel_name': 'ticker'}}],
            },
            extra_rpc_args={},
            mock_api_response={})

    def test_debug(self):
        '''Test debug command'''
        def exec_command():
            self.fb.debug('test message')
        self.send_command_test_helper(
            exec_command,
            expected_command={
                'kind': 'send_message',
                'args': {'message': 'test message', 'message_type': 'debug'},
                'body': [{'kind': 'channel', 'args': {'channel_name': 'ticker'}}],
            },
            extra_rpc_args={},
            mock_api_response={})

    def test_toast(self):
        '''Test toast command'''
        def exec_command():
            self.fb.toast('test message')
        self.send_command_test_helper(
            exec_command,
            expected_command={
                'kind': 'send_message',
                'args': {'message': 'test message', 'message_type': 'info'},
                'body': [{'kind': 'channel', 'args': {'channel_name': 'toast'}}],
            },
            extra_rpc_args={},
            mock_api_response={})

    def test_invalid_message_type(self):
        '''Test message_type validation'''
        def exec_command():
            with self.assertRaises(ValueError) as cm:
                self.fb.message('test', message_type='nope')
            self.assertEqual(
                cm.exception.args[0],
                "Invalid message type: `nope` not in ['assertion', 'busy', 'debug', 'error', 'fun', 'info', 'success', 'warn']")
        self.send_command_test_helper(
            exec_command,
            expected_command=None,
            extra_rpc_args={},
            mock_api_response={})

    def test_invalid_message_channel(self):
        '''Test message channel validation'''
        def exec_command():
            with self.assertRaises(ValueError) as cm:
                self.fb.message('test', channel='nope')
            self.assertEqual(
                cm.exception.args[0],
                "Invalid channel: nope not in ['ticker', 'toast', 'email', 'espeak']")
        self.send_command_test_helper(
            exec_command,
            expected_command=None,
            extra_rpc_args={},
            mock_api_response={})

    def test_read_status(self):
        '''Test read_status command'''
        def exec_command():
            self.fb.read_status()
        self.send_command_test_helper(
            exec_command,
            expected_command={
                'kind': 'read_status',
                'args': {},
            },
            extra_rpc_args={},
            mock_api_response={})

    def test_read_sensor(self):
        '''Test read_sensor command'''
        def exec_command():
            self.fb.read_sensor('Tool Verification')
        self.send_command_test_helper(
            exec_command,
            expected_command={
                'kind': 'read_pin',
                'args': {
                    'pin_mode': 0,
                    'label': '---',
                    'pin_number': {
                        'kind': 'named_pin',
                        'args': {'pin_type': 'Sensor', 'pin_id': 123},
                    },
                },
            },
            extra_rpc_args={},
            mock_api_response=[{'id': 123, 'label': 'Tool Verification', 'mode': 0}])

    def test_read_sensor_not_found(self):
        '''Test read_sensor command: sensor not found'''
        def exec_command():
            self.fb.read_sensor('Temperature')
        self.send_command_test_helper(
            exec_command,
            expected_command=None,
            extra_rpc_args={},
            mock_api_response=[{'label': 'Tool Verification'}])
        self.assertEqual(self.fb.state.error, "ERROR: 'Temperature' not in sensors: ['Tool Verification'].")

    def test_assertion(self):
        '''Test assertion command'''
        def exec_command():
            self.fb.assertion('return true', 'abort')
        self.send_command_test_helper(
            exec_command,
            expected_command={
                'kind': 'assertion',
                'args': {
                    'assertion_type': 'abort',
                    'lua': 'return true',
                    '_then': {'kind': 'nothing', 'args': {}},
                }
            },
            extra_rpc_args={},
            mock_api_response={})

    def test_assertion_with_recovery_sequence(self):
        '''Test assertion command with recovery sequence'''
        def exec_command():
            self.fb.assertion('return true', 'abort', 'Recovery Sequence')
        self.send_command_test_helper(
            exec_command,
            expected_command={
                'kind': 'assertion',
                'args': {
                    'assertion_type': 'abort',
                    'lua': 'return true',
                    '_then': {'kind': 'execute', 'args': {'sequence_id': 123}},
                }
            },
            extra_rpc_args={},
            mock_api_response=[{'id': 123, 'name': 'Recovery Sequence'}])

    def test_assertion_recovery_sequence_not_found(self):
        '''Test assertion command: recovery sequence not found'''
        def exec_command():
            self.fb.assertion('return true', 'abort', 'Recovery Sequence')
        self.send_command_test_helper(
            exec_command,
            expected_command=None,
            extra_rpc_args={},
            mock_api_response=[])
        self.assertEqual(self.fb.state.error, "ERROR: 'Recovery Sequence' not in sequences: [].")

    def test_assertion_invalid_assertion_type(self):
        '''Test assertion command: invalid assertion type'''
        def exec_command():
            with self.assertRaises(ValueError) as cm:
                self.fb.assertion('return true', 'nope')
            self.assertEqual(
                cm.exception.args[0],
                "Invalid assertion_type: nope not in ['abort', 'recover', 'abort_recover', 'continue']")
        self.send_command_test_helper(
            exec_command,
            expected_command=None,
            extra_rpc_args={},
            mock_api_response={})

    def test_wait(self):
        '''Test wait command'''
        def exec_command():
            self.fb.wait(123)
        self.send_command_test_helper(
            exec_command,
            expected_command={
                'kind': 'wait',
                'args': {'milliseconds': 123},
            },
            extra_rpc_args={},
            mock_api_response={})

    def test_unlock(self):
        '''Test unlock command'''
        def exec_command():
            self.fb.unlock()
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
        def exec_command():
            self.fb.e_stop()
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
        def exec_command():
            self.fb.find_home()
        self.send_command_test_helper(
            exec_command,
            expected_command={
                'kind': 'find_home',
                'args': {'axis': 'all', 'speed': 100},
            },
            extra_rpc_args={},
            mock_api_response={})

    def test_find_home_speed_error(self):
        '''Test find_home command: speed error'''
        def exec_command():
            self.fb.find_home('all', 0)
        self.send_command_test_helper(
            exec_command,
            expected_command=None,
            extra_rpc_args={},
            mock_api_response={})
        self.assertEqual(self.fb.state.error, 'ERROR: Speed constrained to 1-100.')

    def test_find_home_invalid_axis(self):
        '''Test find_home command: invalid axis'''
        def exec_command():
            with self.assertRaises(ValueError) as cm:
                self.fb.find_home('nope')
            self.assertEqual(
                cm.exception.args[0],
                "Invalid axis: nope not in ['x', 'y', 'z', 'all']")
        self.send_command_test_helper(
            exec_command,
            expected_command=None,
            extra_rpc_args={},
            mock_api_response={})

    def test_set_home(self):
        '''Test set_home command'''
        def exec_command():
            self.fb.set_home()
        self.send_command_test_helper(
            exec_command,
            expected_command={
                'kind': 'zero',
                'args': {'axis': 'all'},
            },
            extra_rpc_args={},
            mock_api_response={})

    def test_toggle_peripheral(self):
        '''Test toggle_peripheral command'''
        def exec_command():
            self.fb.toggle_peripheral('New Peripheral')
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
            mock_api_response=[{'label': 'New Peripheral', 'id': 123}])

    def test_toggle_peripheral_not_found(self):
        '''Test toggle_peripheral command: peripheral not found'''
        def exec_command():
            self.fb.toggle_peripheral('New Peripheral')
        self.send_command_test_helper(
            exec_command,
            expected_command=None,
            extra_rpc_args={},
            mock_api_response=[])
        self.assertEqual(self.fb.state.error, 'ERROR: \'New Peripheral\' not in peripherals: [].')

    def test_on_digital(self):
        '''Test on command: digital'''
        def exec_command():
            self.fb.on(13)
        self.send_command_test_helper(
            exec_command,
            expected_command={
                'kind': 'write_pin',
                'args': {
                    'pin_value': 1,
                    'pin_mode': 0,
                    'pin_number': 13,
                },
            },
            extra_rpc_args={},
            mock_api_response={})

    def test_off(self):
        '''Test off command'''
        def exec_command():
            self.fb.off(13)
        self.send_command_test_helper(
            exec_command,
            expected_command={
                'kind': 'write_pin',
                'args': {
                    'pin_value': 0,
                    'pin_mode': 0,
                    'pin_number': 13,
                },
            },
            extra_rpc_args={},
            mock_api_response={})

    def test_move(self):
        '''Test move command'''
        def exec_command():
            self.fb.move(1, 2, 3)
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
            extra_rpc_args={},
            mock_api_response={})

    def test_reboot(self):
        '''Test reboot command'''
        def exec_command():
            self.fb.reboot()
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
        def exec_command():
            self.fb.shutdown()
        self.send_command_test_helper(
            exec_command,
            expected_command={
                'kind': 'power_off',
                'args': {},
            },
            extra_rpc_args={},
            mock_api_response={})

    def test_find_axis_length(self):
        '''Test find_axis_length command'''
        def exec_command():
            self.fb.find_axis_length()
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
        def exec_command():
            self.fb.control_peripheral('New Peripheral', 1)
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
            mock_api_response=[{'label': 'New Peripheral', 'mode': 0, 'id': 123}])

    def test_control_peripheral_not_found(self):
        '''Test control_peripheral command: peripheral not found'''
        def exec_command():
            self.fb.control_peripheral('New Peripheral', 1)
        self.send_command_test_helper(
            exec_command,
            expected_command=None,
            extra_rpc_args={},
            mock_api_response=[{'label': 'Pump'}, {'label': 'Lights'}])
        self.assertEqual(self.fb.state.error, "ERROR: 'New Peripheral' not in peripherals: ['Pump', 'Lights'].")

    def test_measure_soil_height(self):
        '''Test measure_soil_height command'''
        def exec_command():
            self.fb.measure_soil_height()
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
        def exec_command():
            self.fb.detect_weeds()
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
        def exec_command():
            self.fb.calibrate_camera()
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
        def exec_command():
            self.fb.sequence('My Sequence')
        self.send_command_test_helper(
            exec_command,
            expected_command={
                'kind': 'execute',
                'args': {'sequence_id': 123},
            },
            extra_rpc_args={},
            mock_api_response=[{'name': 'My Sequence', 'id': 123}])

    def test_sequence_not_found(self):
        '''Test sequence command: sequence not found'''
        def exec_command():
            self.fb.sequence('My Sequence')
        self.send_command_test_helper(
            exec_command,
            expected_command=None,
            extra_rpc_args={},
            mock_api_response=[{'name': 'Water'}])
        self.assertEqual(self.fb.state.error, "ERROR: 'My Sequence' not in sequences: ['Water'].")

    def test_take_photo(self):
        '''Test take_photo command'''
        def exec_command():
            self.fb.take_photo()
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
        def exec_command():
            self.fb.control_servo(4, 100)
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

    def test_control_servo_error(self):
        '''Test control_servo command: error'''
        def exec_command():
            self.fb.control_servo(4, 200)
        self.send_command_test_helper(
            exec_command,
            expected_command=None,
            extra_rpc_args={},
            mock_api_response={'mode': 0})

    def test_get_xyz(self):
        '''Test get_xyz command'''
        def exec_command():
            self.fb.state.last_messages['status'] = {
                'location_data': {'position': {'x': 1, 'y': 2, 'z': 3}},
            }
            position = self.fb.get_xyz()
            self.assertEqual(position, {'x': 1, 'y': 2, 'z': 3})
        self.send_command_test_helper(
            exec_command,
            expected_command={
                'kind': 'read_status',
                'args': {},
            },
            extra_rpc_args={},
            mock_api_response={})

    def test_get_xyz_no_status(self):
        '''Test get_xyz command: no status'''
        def exec_command():
            self.fb.state.last_messages['status'] = None
            position = self.fb.get_xyz()
            self.assertIsNone(position)
        self.send_command_test_helper(
            exec_command,
            expected_command={
                'kind': 'read_status',
                'args': {},
            },
            extra_rpc_args={},
            mock_api_response={})

    def test_check_position(self):
        '''Test check_position command: at position'''
        def exec_command():
            self.fb.state.last_messages['status'] = {
                'location_data': {'position': {'x': 1, 'y': 2, 'z': 3}},
            }
            at_position = self.fb.check_position(1, 2, 3, 0)
            self.assertTrue(at_position)
        self.send_command_test_helper(
            exec_command,
            expected_command={
                'kind': 'read_status',
                'args': {},
            },
            extra_rpc_args={},
            mock_api_response={})

    def test_check_position_false(self):
        '''Test check_position command: not at position'''
        def exec_command():
            self.fb.state.last_messages['status'] = {
                'location_data': {'position': {'x': 1, 'y': 2, 'z': 3}},
            }
            at_position = self.fb.check_position(0, 0, 0, 2)
            self.assertFalse(at_position)
        self.send_command_test_helper(
            exec_command,
            expected_command={
                'kind': 'read_status',
                'args': {},
            },
            extra_rpc_args={},
            mock_api_response={})

    def test_check_position_no_status(self):
        '''Test check_position command: no status'''
        def exec_command():
            self.fb.state.last_messages['status'] = None
            at_position = self.fb.check_position(0, 0, 0, 2)
            self.assertFalse(at_position)
        self.send_command_test_helper(
            exec_command,
            expected_command={
                'kind': 'read_status',
                'args': {},
            },
            extra_rpc_args={},
            mock_api_response={})

    def test_mount_tool(self):
        '''Test mount_tool command'''
        def exec_command():
            self.fb.mount_tool('Weeder')
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
        def exec_command():
            self.fb.dismount_tool()
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
        def exec_command():
            self.fb.water(123)
        self.send_command_test_helper(
            exec_command,
            expected_command={
                'kind': 'lua',
                'args': {'lua': '''plant = api({
                method = "GET",
                url = "/api/points/123"
            })
            water(plant)'''},
            },
            extra_rpc_args={},
            mock_api_response={})

    def test_dispense(self):
        '''Test dispense command'''
        def exec_command():
            self.fb.dispense(100, 'Weeder', 4)
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

    @patch('requests.request')
    def helper_get_seed_tray_cell(self, *args, **kwargs):
        '''Test helper for get_seed_tray_cell command'''
        mock_request = args[0]
        tray_data = kwargs['tray_data']
        cell = kwargs['cell']
        expected_xyz = kwargs['expected_xyz']
        mock_response = Mock()
        mock_api_response = [
            {
                'id': 123,
                'name': 'Seed Tray',
                'pointer_type': '', # not an actual data field
            },
            {
                'pointer_type': 'ToolSlot',
                'pullout_direction': 1,
                'x': 0,
                'y': 0,
                'z': 0,
                'tool_id': 123,
                'name': '', # not an actual data field
                **tray_data,
            },
        ]
        mock_response.json.return_value = mock_api_response
        mock_response.status_code = 200
        mock_response.text = 'text'
        mock_request.return_value = mock_response
        cell = self.fb.get_seed_tray_cell('Seed Tray', cell)
        mock_request.assert_has_calls([
            call(
                'GET',
                'https://my.farm.bot/api/tools',
                headers={
                    'authorization': 'encoded_token_value',
                    'content-type': 'application/json',
                },
                json=None,
            ),
            call().json(),
            call(
                'GET',
                'https://my.farm.bot/api/points',
                headers={
                    'authorization': 'encoded_token_value',
                    'content-type': 'application/json',
                },
                json=None,
            ),
            call().json(),
        ])
        self.assertEqual(cell, expected_xyz, kwargs)

    def test_get_seed_tray_cell(self):
        '''Test get_seed_tray_cell'''
        test_cases = [
            {
                'tray_data': {'pullout_direction': 1},
                'cell': 'a1',
                'expected_xyz': {'x': 1.25, 'y': -18.75, 'z': 0},
            },
            {
                'tray_data': {'pullout_direction': 1},
                'cell': 'b2',
                'expected_xyz': {'x': -11.25, 'y': -6.25, 'z': 0},
            },
            {
                'tray_data': {'pullout_direction': 1},
                'cell': 'd4',
                'expected_xyz': {'x': -36.25, 'y': 18.75, 'z': 0},
            },
            {
                'tray_data': {'pullout_direction': 2},
                'cell': 'a1',
                'expected_xyz': {'x': -36.25, 'y': 18.75, 'z': 0},
            },
            {
                'tray_data': {'pullout_direction': 2},
                'cell': 'b2',
                'expected_xyz': {'x': -23.75, 'y': 6.25, 'z': 0},
            },
            {
                'tray_data': {'pullout_direction': 2},
                'cell': 'd4',
                'expected_xyz': {'x': 1.25, 'y': -18.75, 'z': 0},
            },
            {
                'tray_data': {'pullout_direction': 2, 'x': 100, 'y': 200, 'z': -100},
                'cell': 'd4',
                'expected_xyz': {'x': 101.25, 'y': 181.25, 'z': -100},
            },
        ]
        for test_case in test_cases:
            self.helper_get_seed_tray_cell(**test_case)

    @patch('requests.request')
    def helper_get_seed_tray_cell_error(self, *args, **kwargs):
        '''Test helper for get_seed_tray_cell command errors'''
        mock_request = args[0]
        tray_data = kwargs['tray_data']
        cell = kwargs['cell']
        error = kwargs['error']
        mock_response = Mock()
        mock_api_response =  [
            {
                'id': 123,
                'name': 'Seed Tray',
                'pointer_type': '', # not an actual data field
            },
            {
                'pointer_type': 'ToolSlot',
                'pullout_direction': 1,
                'x': 0,
                'y': 0,
                'z': 0,
                'tool_id': 123,
                'name': '', # not an actual data field
                **tray_data,
            },
        ]
        mock_response.json.return_value = mock_api_response
        mock_response.status_code = 200
        mock_response.text = 'text'
        mock_request.return_value = mock_response
        with self.assertRaises(ValueError) as cm:
            self.fb.get_seed_tray_cell('Seed Tray', cell)
        self.assertEqual(cm.exception.args[0], error)
        mock_request.assert_has_calls([
            call(
                'GET',
                'https://my.farm.bot/api/tools',
                headers={
                    'authorization': 'encoded_token_value',
                    'content-type': 'application/json',
                },
                json=None,
            ),
            call().json(),
            call(
                'GET',
                'https://my.farm.bot/api/points',
                headers={
                    'authorization': 'encoded_token_value',
                    'content-type': 'application/json',
                },
                json=None,
            ),
            call().json(),
        ])

    def test_get_seed_tray_cell_invalid_cell_name(self):
        '''Test get_seed_tray_cell: invalid cell name'''
        self.helper_get_seed_tray_cell_error(
            tray_data={},
            cell='e4',
            error='Seed Tray Cell must be one of **A1** through **D4**',
        )

    def test_get_seed_tray_cell_invalid_pullout_direction(self):
        '''Test get_seed_tray_cell: invalid pullout direction'''
        self.helper_get_seed_tray_cell_error(
            tray_data={'pullout_direction': 0},
            cell='d4',
            error='Seed Tray **SLOT DIRECTION** must be `Positive X` or `Negative X`',
        )

    @patch('requests.request')
    def test_get_seed_tray_cell_no_tray(self, mock_request):
        '''Test get_seed_tray_cell: no seed tray'''
        mock_response = Mock()
        mock_api_response =  []
        mock_response.json.return_value = mock_api_response
        mock_response.status_code = 200
        mock_response.text = 'text'
        mock_request.return_value = mock_response
        result = self.fb.get_seed_tray_cell('Seed Tray', 'a1')
        mock_request.assert_has_calls([
            call(
                'GET',
                'https://my.farm.bot/api/tools',
                headers={
                    'authorization': 'encoded_token_value',
                    'content-type': 'application/json',
                },
                json=None,
            ),
            call().json(),
        ])
        self.assertIsNone(result)

    @patch('requests.request')
    def test_get_seed_tray_cell_not_mounted(self, mock_request):
        '''Test get_seed_tray_cell: seed tray not mounted'''
        mock_response = Mock()
        mock_api_response =  [{
            'id': 123,
            'name': 'Seed Tray',
            'pointer_type': '', # not an actual data field,
        }]
        mock_response.json.return_value = mock_api_response
        mock_response.status_code = 200
        mock_response.text = 'text'
        mock_request.return_value = mock_response
        result = self.fb.get_seed_tray_cell('Seed Tray', 'a1')
        mock_request.assert_has_calls([
            call(
                'GET',
                'https://my.farm.bot/api/tools',
                headers={
                    'authorization': 'encoded_token_value',
                    'content-type': 'application/json',
                },
                json=None,
            ),
            call().json(),
        ])
        self.assertIsNone(result)

    def test_get_job_one(self):
        '''Test get_job command: get one job'''
        def exec_command():
            self.fb.state.last_messages['status'] = {
                'jobs': {
                    'job name': {'status': 'working'},
                },
            }
            job = self.fb.get_job('job name')
            self.assertEqual(job, {'status': 'working'})
        self.send_command_test_helper(
            exec_command,
            expected_command={
                'kind': 'read_status',
                'args': {},
            },
            extra_rpc_args={},
            mock_api_response={})

    def test_get_job_all(self):
        '''Test get_job command: get all jobs'''
        def exec_command():
            self.fb.state.last_messages['status'] = {
                'jobs': {
                    'job name': {'status': 'working'},
                },
            }
            jobs = self.fb.get_job()
            self.assertEqual(jobs, {'job name': {'status': 'working'}})
        self.send_command_test_helper(
            exec_command,
            expected_command={
                'kind': 'read_status',
                'args': {},
            },
            extra_rpc_args={},
            mock_api_response={})

    def test_get_job_no_status(self):
        '''Test get_job command: no status'''
        def exec_command():
            self.fb.state.last_messages['status'] = None
            job = self.fb.get_job('job name')
            self.assertIsNone(job)
        self.send_command_test_helper(
            exec_command,
            expected_command={
                'kind': 'read_status',
                'args': {},
            },
            extra_rpc_args={},
            mock_api_response={})

    def test_set_job(self):
        '''Test set_job command'''
        def exec_command():
            self.fb.set_job('job name', 'working', 50)
        self.send_command_test_helper(
            exec_command,
            expected_command={
                'kind': 'lua',
                'args': {'lua': '''local job_name = "job name"
            set_job(job_name)

            -- Update the job's status and percent:
            set_job(job_name, {
            status = "working",
            percent = 50
            })'''},
            },
            extra_rpc_args={},
            mock_api_response={})

    def test_complete_job(self):
        '''Test complete_job command'''
        def exec_command():
            self.fb.complete_job('job name')
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
        def exec_command():
            self.fb.lua('return true')
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
        def exec_command():
            self.fb.if_statement('pin10', 'is', 0)
        self.send_command_test_helper(
            exec_command,
            expected_command={
                'kind': '_if',
                'args': {
                    'lhs': 'pin10',
                    'op': 'is',
                    'rhs': 0,
                    '_then': {'kind': 'nothing', 'args': {}},
                    '_else': {'kind': 'nothing', 'args': {}},
                }
            },
            extra_rpc_args={},
            mock_api_response=[])

    def test_if_statement_with_named_pin(self):
        '''Test if_statement command with named pin'''
        def exec_command():
            self.fb.if_statement('Lights', 'is', 0, named_pin_type='Peripheral')
        self.send_command_test_helper(
            exec_command,
            expected_command={
                'kind': '_if',
                'args': {
                    'lhs': {
                        'kind': 'named_pin',
                        'args': {'pin_type': 'Peripheral', 'pin_id': 123},
                    },
                    'op': 'is',
                    'rhs': 0,
                    '_then': {'kind': 'nothing', 'args': {}},
                    '_else': {'kind': 'nothing', 'args': {}},
                }
            },
            extra_rpc_args={},
            mock_api_response=[{'id': 123, 'label': 'Lights', 'mode': 0}])

    def test_if_statement_with_named_pin_not_found(self):
        '''Test if_statement command: named pin not found'''
        def exec_command():
            self.fb.if_statement('Lights', 'is', 0, named_pin_type='Peripheral')
        self.send_command_test_helper(
            exec_command,
            expected_command=None,
            extra_rpc_args={},
            mock_api_response=[{'label': 'Pump'}])
        self.assertEqual(self.fb.state.error, "ERROR: 'Lights' not in peripherals: ['Pump'].")

    def test_if_statement_with_sequences(self):
        '''Test if_statement command with sequences'''
        def exec_command():
            self.fb.if_statement('pin10', '<', 0, 'Watering Sequence', 'Drying Sequence')
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
            mock_api_response=[
                {'id': 123, 'name': 'Watering Sequence'},
                {'id': 456, 'name': 'Drying Sequence'},
            ])

    def test_if_statement_with_sequence_not_found(self):
        '''Test if_statement command: sequence not found'''
        def exec_command():
            self.fb.if_statement('pin10', '<', 0, 'Watering Sequence', 'Drying Sequence')
        self.send_command_test_helper(
            exec_command,
            expected_command=None,
            extra_rpc_args={},
            mock_api_response=[])
        self.assertEqual(self.fb.state.error, "ERROR: 'Watering Sequence' not in sequences: [].")

    def test_if_statement_invalid_operator(self):
        '''Test if_statement command: invalid operator'''
        def exec_command():
            with self.assertRaises(ValueError) as cm:
                self.fb.if_statement('pin10', 'nope', 0)
            self.assertEqual(
                cm.exception.args[0],
                "Invalid operator: nope not in ['<', '>', 'is', 'not', 'is_undefined']")
        self.send_command_test_helper(
            exec_command,
            expected_command=None,
            extra_rpc_args={},
            mock_api_response=[])

    def test_if_statement_invalid_variable(self):
        '''Test if_statement command: invalid variable'''
        variables = ["x", "y", "z", *[f"pin{str(i)}" for i in range(70)]]
        def exec_command():
            with self.assertRaises(ValueError) as cm:
                self.fb.if_statement('nope', '<', 0)
            self.assertEqual(
                cm.exception.args[0],
                f"Invalid variable: nope not in {variables}")
        self.send_command_test_helper(
            exec_command,
            expected_command=None,
            extra_rpc_args={},
            mock_api_response=[])

    def test_if_statement_invalid_named_pin_type(self):
        '''Test if_statement command: invalid named pin type'''
        def exec_command():
            with self.assertRaises(ValueError) as cm:
                self.fb.if_statement('pin10', '<', 0, named_pin_type='nope')
            self.assertEqual(
                cm.exception.args[0],
                "Invalid named_pin_type: nope not in ['Peripheral', 'Sensor']")
        self.send_command_test_helper(
            exec_command,
            expected_command=None,
            extra_rpc_args={},
            mock_api_response=[])

    def test_rpc_error(self):
        '''Test rpc error handling'''
        def exec_command():
            self.fb.wait(100)
            self.assertEqual(self.fb.state.error, 'RPC error response received.')
        self.send_command_test_helper(
            exec_command,
            error=True,
            expected_command={
                'kind': 'wait',
                'args': {'milliseconds': 100}},
            extra_rpc_args={},
            mock_api_response=[])

    def test_rpc_response_timeout(self):
        '''Test rpc response timeout handling'''
        def exec_command():
            self.fb.state.last_messages['from_device'] = {'kind': 'rpc_ok', 'args': {'label': 'wrong label'}}
            self.fb.wait(100)
            self.assertEqual(self.fb.state.error, 'Timed out waiting for RPC response.')
        self.send_command_test_helper(
            exec_command,
            expected_command={
                'kind': 'wait',
                'args': {'milliseconds': 100}},
            extra_rpc_args={},
            mock_api_response=[])

    @staticmethod
    def helper_get_print_strings(mock_print):
        '''Test helper to get print call strings.'''
        return [string[1][0] for string in mock_print.mock_calls if len(string[1]) > 0]

    @patch('builtins.print')
    def test_print_status(self, mock_print):
        '''Test print_status.'''
        self.fb.set_verbosity(0)
        self.fb.state.print_status(description="testing")
        mock_print.assert_not_called()
        self.fb.set_verbosity(1)
        self.fb.state.print_status(description="testing")
        call_strings = self.helper_get_print_strings(mock_print)
        self.assertIn('testing', call_strings)
        mock_print.reset_mock()
        self.fb.set_verbosity(2)
        self.fb.state.print_status(endpoint_json=["testing"])
        call_strings = self.helper_get_print_strings(mock_print)
        call_strings = [s.split('(')[0].strip('`') for s in call_strings]
        self.assertIn('[\n    "testing"\n]', call_strings)
        self.assertIn('test_print_status', call_strings)
