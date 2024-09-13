'''
Farmbot class unit tests.
'''

import json
import unittest
from unittest.mock import Mock, patch, call
import requests

from farmbot import Farmbot

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

TOKEN_REQUEST_KWARGS = {
    'headers': {'content-type': 'application/json'},
    'timeout': 0,
}

REQUEST_KWARGS_WITH_PAYLOAD = {
    'headers': {
        'authorization': 'encoded_token_value',
        'content-type': 'application/json'
    },
    'timeout': 0,
}

REQUEST_KWARGS = {
    **REQUEST_KWARGS_WITH_PAYLOAD,
    'json': None,
}


class TestFarmbot(unittest.TestCase):
    '''Farmbot tests'''

    def setUp(self):
        '''Set up method called before each test case'''
        self.fb = Farmbot()
        self.fb.set_token(MOCK_TOKEN)
        self.fb.set_verbosity(0)
        self.fb.state.test_env = True
        self.fb.set_timeout(0, 'all')
        self.fb.clear_cache()

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
            url='https://my.farm.bot/api/tokens',
            **TOKEN_REQUEST_KWARGS,
            json={'user': {'email': 'test_email@gmail.com',
                           'password': 'test_pass_123'}},
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
            url='https://staging.farm.bot/api/tokens',
            **TOKEN_REQUEST_KWARGS,
            json={'user': {'email': 'test_email@gmail.com',
                           'password': 'test_pass_123'}},
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
            url='https://my.farm.bot/api/tokens',
            **TOKEN_REQUEST_KWARGS,
            json={'user': {'email': 'email@gmail.com',
                           'password': 'test_pass_123'}},
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
            url='https://my.farm.bot/api/tokens',
            **TOKEN_REQUEST_KWARGS,
            json={'user': {'email': 'email@gmail.com',
                           'password': 'test_pass_123'}},
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
            method='GET',
            url='https://my.farm.bot/api/device',
            **REQUEST_KWARGS,
        )
        self.assertEqual(response, error_msg)

    def test_api_get_errors(self):
        '''Test api_get errors'''
        msg_404 = 'CLIENT ERROR 404: The specified endpoint does not exist.'
        msg_404 += ' ({\n  "error": "error"\n})'
        self.helper_api_get_error(
            status_code=404,
            error_msg=msg_404
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
        mock_response.json.side_effect = requests.exceptions.JSONDecodeError(
            '', '', 0)
        mock_request.return_value = mock_response
        response = self.fb.api_get('device')
        mock_request.assert_called_once_with(
            method='GET',
            url='https://my.farm.bot/api/device',
            **REQUEST_KWARGS,
        )
        self.assertEqual(
            response,
            'CLIENT ERROR 404: The specified endpoint does not exist. (error string)')

    @patch('requests.request')
    def test_api_string_error_response_handling_html(self, mock_request):
        '''Test API html string response errors'''
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.reason = 'reason'
        mock_response.text = '<html><h1>error0</h1><h2>error1</h2></html>'
        mock_response.json.side_effect = requests.exceptions.JSONDecodeError(
            '', '', 0)
        mock_request.return_value = mock_response
        response = self.fb.api_get('device')
        mock_request.assert_called_once_with(
            method='GET',
            url='https://my.farm.bot/api/device',
            **REQUEST_KWARGS,
        )
        self.assertEqual(
            response,
            'CLIENT ERROR 404: The specified endpoint does not exist. (error0 error1)')

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
            method='GET',
            url='https://my.farm.bot/api/device',
            **REQUEST_KWARGS,
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
            method='GET',
            url='https://my.farm.bot/api/peripherals/12345',
            **REQUEST_KWARGS,
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
            method='PATCH',
            url='https://my.farm.bot/api/device',
            **REQUEST_KWARGS_WITH_PAYLOAD,
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
            method='POST',
            url='https://my.farm.bot/api/points',
            **REQUEST_KWARGS_WITH_PAYLOAD,
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
            method='DELETE',
            url='https://my.farm.bot/api/points/12345',
            **REQUEST_KWARGS,
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
    def helper_test_get_curve(self, *args, **kwargs):
        '''get_curve function test helper'''
        mock_request = args[0]
        mock_response = Mock()
        mock_response.json.return_value = {
            'name': 'Curve 0',
            **kwargs.get('api_data'),
        }
        mock_response.status_code = 200
        mock_response.text = 'text'
        mock_request.return_value = mock_response
        curve_info = self.fb.get_curve(12345)
        mock_request.assert_called_once_with(
            method='GET',
            url='https://my.farm.bot/api/curves/12345',
            **REQUEST_KWARGS,
        )
        self.assertEqual(curve_info['name'], 'Curve 0')
        self.assertEqual(curve_info['type'], kwargs.get('type'))
        self.assertEqual(curve_info['unit'], kwargs.get('unit'))
        self.assertEqual(curve_info.day(50), kwargs.get('value'))

    def test_get_curve(self):
        '''test get_curve function'''
        self.helper_test_get_curve(
            api_data={
                'type': 'water',
                'data': {'1': 1, '100': 100},
            },
            type='water',
            unit='mL',
            value=50,
        )
        self.helper_test_get_curve(
            api_data={
                'type': 'water',
                'data': {'100': 1, '200': 100},
            },
            type='water',
            unit='mL',
            value=1,
        )
        self.helper_test_get_curve(
            api_data={
                'type': 'water',
                'data': {'1': 1, '2': 100},
            },
            type='water',
            unit='mL',
            value=100,
        )
        self.helper_test_get_curve(
            api_data={
                'type': 'height',
                'data': {'1': 1, '50': 500, '100': 100},
            },
            type='height',
            unit='mm',
            value=500,
        )

    @patch('requests.request')
    def test_get_curve_error(self, mock_request):
        '''test get_curve function: error'''
        mock_response = Mock()
        mock_response.json.return_value = None
        mock_response.status_code = 400
        mock_response.text = 'text'
        mock_request.return_value = mock_response
        curve_info = self.fb.get_curve(12345)
        mock_request.assert_called_once_with(
            method='GET',
            url='https://my.farm.bot/api/curves/12345',
            **REQUEST_KWARGS,
        )
        self.assertIsNone(curve_info)

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
            method='GET',
            url='https://my.farm.bot/api/fbos_config',
            **REQUEST_KWARGS,
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
            method='GET',
            url='https://my.farm.bot/api/firmware_config',
            **REQUEST_KWARGS,
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
        self.fb.log('test message', 'info', ['toast'])
        mock_request.assert_called_once_with(
            method='POST',
            url='https://my.farm.bot/api/logs',
            **REQUEST_KWARGS_WITH_PAYLOAD,
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
            topic = 'bot/device_0/topic'
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
        self.assertEqual(self.fb.state.last_messages['topic'], [{
            'topic': 'bot/device_0/topic',
            'content': {'message': 'test message'},
        }])

    @patch('paho.mqtt.client.Client')
    def test_listen_diff_only(self, mock_mqtt):
        '''Test listen command: diff_only'''
        mock_client = Mock()
        mock_mqtt.return_value = mock_client
        self.fb.listen(message_options={'diff_only': True})

        class MockMessageFirst:
            '''Mock message class'''
            topic = 'bot/device_0/topic'
            payload = '{"message": "test message", "i": 0}'
        mock_client.on_message('', '', MockMessageFirst())

        class MockMessageSecond:
            '''Mock message class'''
            topic = 'bot/device_0/topic'
            payload = '{"message": "test message", "i": 1}'
        mock_client.on_message('', '', MockMessageSecond())
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
        self.assertEqual(self.fb.state.last_messages['topic'], [
            {'topic': 'bot/device_0/topic',
             'content': {'message': 'test message', 'i': 0}},
            {'topic': 'bot/device_0/topic',
             'content': {'message': 'test message', 'i': 1}},
        ])
        self.assertEqual(self.fb.state.last_messages['topic_diffs'], [
            {'i': 1},
        ])

    @patch('paho.mqtt.client.Client')
    def test_listen_with_filters(self, mock_mqtt):
        '''Test listen command with filters'''
        mock_client = Mock()
        mock_mqtt.return_value = mock_client
        self.fb.listen(message_options={'filters': {
            'topic': 'sync/Point',
            'content': {'body.pointerType': 'Plant'}}})

        class MockMessageMiss:
            '''Mock message class'''
            topic = 'bot/device_0/topic'
            payload = '{"message": "test message"}'
        mock_client.on_message('', '', MockMessageMiss())

        class MockMessageAlsoMiss:
            '''Mock message class'''
            topic = 'bot/device_0/sync/Point/123'
            payload = json.dumps({'body': {'pointerType': 'Weed'}})
        mock_client.on_message('', '', MockMessageAlsoMiss())

        class MockMessageMatch:
            '''Mock message class'''
            topic = 'bot/device_0/sync/Point/1234'
            payload = json.dumps({'body': {'pointerType': 'Plant'}})
        mock_client.on_message('', '', MockMessageMatch())
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
        self.assertEqual(self.fb.state.last_messages['sync'], [{
            'topic': 'bot/device_0/sync/Point/1234',
            'content': {'body': {'pointerType': 'Plant'}},
        }])

    @patch('math.inf', 0.1)
    @patch('paho.mqtt.client.Client')
    def test_listen_for_status_changes(self, mock_mqtt):
        '''Test listen_for_status_changes command'''
        self.maxDiff = None
        i = 0

        mock_client = Mock()
        mock_mqtt.return_value = mock_client

        class MockMessage:
            '''Mock message class'''

            def __init__(self):
                self.topic = 'bot/device_0/status'
                payload = {
                    'location_data': {
                        'position': {
                            'x': i,
                            'y': i + 10,
                            'z': 100,
                        }}}
                if i == 2:
                    payload['location_data']['position']['extra'] = {'idx': 2}
                if i == 3:
                    payload['location_data']['position']['extra'] = {'idx': 3}
                self.payload = json.dumps(payload)

        def patched_sleep(_seconds):
            '''Patched sleep function'''
            nonlocal i
            mock_message = MockMessage()
            mock_client.on_message('', '', mock_message)
            i += 1

        with patch('time.sleep', new=patched_sleep):
            self.fb.listen_for_status_changes(
                stop_count=5,
                path='location_data.position')

        self.assertEqual(self.fb.state.last_messages['status'], [
            {
                'topic': 'bot/device_0/status',
                'content': {'location_data': {'position': {'x': 0, 'y': 10, 'z': 100}}}},
            {
                'topic': 'bot/device_0/status',
                'content': {'location_data': {'position': {'x': 1, 'y': 11, 'z': 100}}}},
            {
                'topic': 'bot/device_0/status',
                'content': {'location_data': {'position': {
                    'extra': {'idx': 2}, 'x': 2, 'y': 12, 'z': 100}}}},
            {
                'topic': 'bot/device_0/status',
                'content': {'location_data': {'position': {
                    'extra': {'idx': 3}, 'x': 3, 'y': 13, 'z': 100}}}},
            {
                'topic': 'bot/device_0/status',
                'content': {'location_data': {'position': {'x': 4, 'y': 14, 'z': 100}}}},
        ])
        self.assertEqual(self.fb.state.last_messages['status_diffs'], [
            {'x': 1, 'y': 11},
            {'extra': {'idx': 2}, 'x': 2, 'y': 12},
            {'extra': {'idx': 3}, 'x': 3, 'y': 13},
            {'x': 4, 'y': 14},
        ])
        self.assertEqual(self.fb.state.last_messages['status_excerpt'], [
            {'x': 0, 'y': 10, 'z': 100},
            {'x': 1, 'y': 11, 'z': 100},
            {'extra': {'idx': 2}, 'x': 2, 'y': 12, 'z': 100},
            {'extra': {'idx': 3}, 'x': 3, 'y': 13, 'z': 100},
            {'x': 4, 'y': 14, 'z': 100},
        ])

    @patch('math.inf', 0.1)
    @patch('paho.mqtt.client.Client')
    def test_listen_for_status_changes_single_value(self, mock_mqtt):
        '''Test listen_for_status_changes command: single value'''
        self.maxDiff = None
        i = 0

        mock_client = Mock()
        mock_mqtt.return_value = mock_client

        class MockMessage:
            '''Mock message class'''

            def __init__(self):
                self.topic = 'bot/device_0/status'
                payload = {'location_data': {'position': {'x': i}}}
                self.payload = json.dumps(payload)

        def patched_sleep(_seconds):
            '''Patched sleep function'''
            nonlocal i
            mock_message = MockMessage()
            mock_client.on_message('', '', mock_message)
            i += 1

        with patch('time.sleep', new=patched_sleep):
            self.fb.listen_for_status_changes(
                stop_count=5,
                path='location_data.position.x')

        self.assertEqual(self.fb.state.last_messages['status_diffs'],
                         [1, 2, 3, 4])
        self.assertEqual(self.fb.state.last_messages['status_excerpt'],
                         [0, 1, 2, 3, 4])

    @patch('paho.mqtt.client.Client')
    def test_listen_clear_last(self, mock_mqtt):
        '''Test listen command: clear last message'''
        mock_client = Mock()
        mock_mqtt.return_value = mock_client
        self.fb.state.last_messages = [
            {'#': {'topic': '', 'content': "message"}},
        ]
        self.fb.state.test_env = False
        self.fb.listen()
        self.assertEqual(len(self.fb.state.last_messages['#']), 0)

    @patch('paho.mqtt.client.Client')
    def test_listen_interrupt(self, mock_mqtt):
        '''Test listen command: interrupt'''
        mock_client = Mock()
        mock_mqtt.return_value = mock_client
        self.fb.state.test_env = False

        def patched_sleep(_seconds):
            '''Patched sleep function'''
            raise KeyboardInterrupt
        with patch('time.sleep', new=patched_sleep):
            self.fb.listen(stop_count=100)
        mock_client.loop_stop.assert_called_once()

    @patch('paho.mqtt.client.Client')
    def test_publish_apply_label(self, mock_mqtt):
        '''Test publish command: set uuid'''
        mock_client = Mock()
        mock_mqtt.return_value = mock_client
        self.fb.state.test_env = False
        self.fb.publish({'kind': 'sync', 'args': {}})
        label = self.fb.state.last_published.get('args', {}).get('label')
        self.assertNotIn(label, ['test', '', None])

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
        self.fb.state.last_messages['from_device'] = [{
            'topic': '',
            'content': {
                'kind': 'rpc_error' if error else 'rpc_ok',
                'args': {'label': 'test'},
            },
        }]
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
            self.assertNotEqual(
                self.fb.state.error,
                'RPC error response received.')

    def test_message(self):
        '''Test message command'''
        def exec_command():
            self.fb.send_message('test message', 'info')
        self.send_command_test_helper(
            exec_command,
            expected_command={
                'kind': 'send_message',
                'args': {'message': 'test message', 'message_type': 'info'},
                'body': [],
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
                'body': [],
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
                self.fb.send_message('test', message_type='nope')
            msg = 'Invalid message type: `nope` not in '
            msg += "['assertion', 'busy', 'debug', 'error', 'fun', 'info', 'success', 'warn']"
            self.assertEqual(cm.exception.args[0], msg)
        self.send_command_test_helper(
            exec_command,
            expected_command=None,
            extra_rpc_args={},
            mock_api_response={})

    def test_invalid_message_channel(self):
        '''Test message channel validation'''
        def exec_command():
            with self.assertRaises(ValueError) as cm:
                self.fb.send_message('test', channels=['nope'])
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
            self.fb.state.last_messages['status'] = [{
                'topic': '',
                'content': {'location_data': {'position': {'x': 100}}},
            }]
            result = self.fb.read_status()
            self.assertEqual(
                result,
                {'location_data': {'position': {'x': 100}}})
        self.send_command_test_helper(
            exec_command,
            expected_command={
                'kind': 'read_status',
                'args': {},
            },
            extra_rpc_args={},
            mock_api_response={})

    def test_read_status_path(self):
        '''Test read_status command: specific path'''
        def exec_command():
            self.fb.state.last_messages['status'] = [{
                'topic': '',
                'content': {
                    'location_data': {'position': {'x': 100}},
                },
            }]
            result = self.fb.read_status('location_data.position.x')
            self.assertEqual(result, 100)
        self.send_command_test_helper(
            exec_command,
            expected_command={
                'kind': 'read_status',
                'args': {},
            },
            extra_rpc_args={},
            mock_api_response={})

    def test_read_pin(self):
        '''Test read_pin command'''
        def exec_command():
            self.fb.read_pin(13)
        self.send_command_test_helper(
            exec_command,
            expected_command={
                'kind': 'read_pin',
                'args': {
                    'pin_number': 13,
                    'label': '---',
                    'pin_mode': 0,
                },
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
        self.assertEqual(
            self.fb.state.error,
            "ERROR: 'Temperature' not in sensors: ['Tool Verification'].")

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
        self.assertEqual(
            self.fb.state.error,
            "ERROR: 'Recovery Sequence' not in sequences: [].")

    def test_assertion_invalid_assertion_type(self):
        '''Test assertion command: invalid assertion type'''
        def exec_command():
            with self.assertRaises(ValueError) as cm:
                self.fb.assertion('return true', 'nope')
            msg = 'Invalid assertion_type: nope not in '
            msg += "['abort', 'recover', 'abort_recover', 'continue']"
            self.assertEqual(cm.exception.args[0], msg)
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
        self.assertEqual(
            self.fb.state.error,
            'ERROR: Speed constrained to 1-100.')

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
        self.assertEqual(
            self.fb.state.error,
            'ERROR: \'New Peripheral\' not in peripherals: [].')

    @patch('requests.request')
    @patch('paho.mqtt.client.Client')
    def test_toggle_peripheral_use_cache(self, mock_mqtt, mock_request):
        '''Test toggle_peripheral command: use cache'''
        mock_client = Mock()
        mock_mqtt.return_value = mock_client
        mock_response = Mock()
        mock_response.json.return_value = [
            {'label': 'Peripheral 4', 'id': 123},
            {'label': 'Peripheral 5', 'id': 456}
        ]
        mock_response.status_code = 200
        mock_response.text = 'text'
        mock_request.return_value = mock_response
        # save cache
        self.fb.toggle_peripheral('Peripheral 4')
        mock_request.assert_called()
        mock_client.publish.assert_called()
        mock_request.reset_mock()
        mock_client.reset_mock()
        # use cache
        self.fb.toggle_peripheral('Peripheral 5')
        mock_request.assert_not_called()
        mock_client.publish.assert_called()
        mock_request.reset_mock()
        mock_client.reset_mock()
        # clear cache
        self.fb.toggle_peripheral('Peripheral 6')
        mock_request.assert_not_called()
        mock_client.publish.assert_not_called()
        mock_request.reset_mock()
        mock_client.reset_mock()
        # save cache
        self.fb.toggle_peripheral('Peripheral 4')
        mock_request.assert_called()
        mock_client.publish.assert_called()
        mock_request.reset_mock()
        mock_client.reset_mock()

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
            self.fb.move()
        self.send_command_test_helper(
            exec_command,
            expected_command={
                'kind': 'move',
                'args': {},
                'body': [],
            },
            extra_rpc_args={},
            mock_api_response={})

    def test_move_extras(self):
        '''Test move command with extras'''
        def exec_command():
            self.fb.move(1, 2, 3, safe_z=True, speed=50)
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
                    {'kind': 'speed_overwrite', 'args': {
                        'axis': 'x',
                        'speed_setting': {'kind': 'numeric', 'args': {'number': 50}}}},
                    {'kind': 'speed_overwrite', 'args': {
                        'axis': 'y',
                        'speed_setting': {'kind': 'numeric', 'args': {'number': 50}}}},
                    {'kind': 'speed_overwrite', 'args': {
                        'axis': 'z',
                        'speed_setting': {'kind': 'numeric', 'args': {'number': 50}}}},
                    {'kind': 'safe_z', 'args': {}},
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

    def test_write_pin(self):
        '''Test write_pin command'''
        def exec_command():
            self.fb.write_pin(13, 1, 'analog')
        self.send_command_test_helper(
            exec_command,
            expected_command={
                'kind': 'write_pin',
                'args': {
                    'pin_number': 13,
                    'pin_value': 1,
                    'pin_mode': 1,
                },
            },
            extra_rpc_args={},
            mock_api_response={})

    def test_write_pin_invalid_mode(self):
        '''Test write_pin command: invalid mode'''
        def exec_command():
            with self.assertRaises(ValueError) as cm:
                self.fb.write_pin(13, 1, 1)
            self.assertEqual(
                cm.exception.args[0],
                "Invalid mode: 1 not in ['digital', 'analog']")
        self.send_command_test_helper(
            exec_command,
            expected_command=None,
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

    def test_control_peripheral_analog(self):
        '''Test control_peripheral command: analog'''
        def exec_command():
            self.fb.control_peripheral('New Peripheral', 1, 'analog')
        self.send_command_test_helper(
            exec_command,
            expected_command={
                'kind': 'write_pin',
                'args': {
                    'pin_value': 1,
                    'pin_mode': 1,
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
        self.assertEqual(
            self.fb.state.error,
            "ERROR: 'New Peripheral' not in peripherals: ['Pump', 'Lights'].")

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
        self.assertEqual(
            self.fb.state.error,
            "ERROR: 'My Sequence' not in sequences: ['Water'].")

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
            self.fb.state.last_messages['status'] = [{
                'topic': '',
                'content': {
                    'location_data': {'position': {'x': 1, 'y': 2, 'z': 3}},
                },
            }]
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
            self.fb.state.last_messages['status'] = []
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
            self.fb.state.last_messages['status'] = [{
                'topic': '',
                'content': {
                    'location_data': {'position': {'x': 1, 'y': 2, 'z': 3}},
                },
            }]
            at_position = self.fb.check_position({'x': 1, 'y': 2, 'z': 3}, 0)
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
            self.fb.state.last_messages['status'] = [{
                'topic': '',
                'content': {
                    'location_data': {'position': {'x': 1, 'y': 2, 'z': 3}},
                },
            }]
            at_position = self.fb.check_position({'x': 0, 'y': 0, 'z': 0}, 2)
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
            self.fb.state.last_messages['status'] = []
            at_position = self.fb.check_position({'x': 0, 'y': 0, 'z': 0}, 2)
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
            self.fb.dispense(100)
        self.send_command_test_helper(
            exec_command,
            expected_command={
                'kind': 'lua',
                'args': {
                    'lua': 'dispense(100)',
                },
            },
            extra_rpc_args={},
            mock_api_response={})

    def test_dispense_all_args(self):
        '''Test dispense command with all args'''
        def exec_command():
            self.fb.dispense(100, 'Nutrient Sprayer', 4)
        self.send_command_test_helper(
            exec_command,
            expected_command={
                'kind': 'lua',
                'args': {
                    'lua': 'dispense(100, {tool_name = "Nutrient Sprayer", pin = 4})',
                },
            },
            extra_rpc_args={},
            mock_api_response={})

    def test_dispense_only_pin(self):
        '''Test dispense command'''
        def exec_command():
            self.fb.dispense(100, pin=4)
        self.send_command_test_helper(
            exec_command,
            expected_command={
                'kind': 'lua',
                'args': {
                    'lua': 'dispense(100, {pin = 4})',
                },
            },
            extra_rpc_args={},
            mock_api_response={})

    def test_dispense_only_tool_name(self):
        '''Test dispense command'''
        def exec_command():
            self.fb.dispense(100, "Nutrient Sprayer")
        self.send_command_test_helper(
            exec_command,
            expected_command={
                'kind': 'lua',
                'args': {
                    'lua': 'dispense(100, {tool_name = "Nutrient Sprayer"})',
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
        self.fb.clear_cache()
        mock_response = Mock()
        mock_api_response = [
            {
                'id': 123,
                'name': 'Seed Tray',
                'pointer_type': '',  # not an actual data field
            },
            {
                'pointer_type': 'ToolSlot',
                'pullout_direction': 1,
                'x': 0,
                'y': 0,
                'z': 0,
                'tool_id': 123,
                'name': '',  # not an actual data field
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
                method='GET',
                url='https://my.farm.bot/api/tools',
                **REQUEST_KWARGS,
            ),
            call().json(),
            call(
                method='GET',
                url='https://my.farm.bot/api/points',
                **REQUEST_KWARGS,
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
        mock_api_response = [
            {
                'id': 123,
                'name': 'Seed Tray',
                'pointer_type': '',  # not an actual data field
            },
            {
                'pointer_type': 'ToolSlot',
                'pullout_direction': 1,
                'x': 0,
                'y': 0,
                'z': 0,
                'tool_id': 123,
                'name': '',  # not an actual data field
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
                method='GET',
                url='https://my.farm.bot/api/tools',
                **REQUEST_KWARGS,
            ),
            call().json(),
            call(
                method='GET',
                url='https://my.farm.bot/api/points',
                **REQUEST_KWARGS,
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
        mock_api_response = []
        mock_response.json.return_value = mock_api_response
        mock_response.status_code = 200
        mock_response.text = 'text'
        mock_request.return_value = mock_response
        result = self.fb.get_seed_tray_cell('Seed Tray', 'a1')
        mock_request.assert_has_calls([
            call(
                method='GET',
                url='https://my.farm.bot/api/tools',
                **REQUEST_KWARGS,
            ),
            call().json(),
        ])
        self.assertIsNone(result)

    @patch('requests.request')
    def test_get_seed_tray_cell_not_mounted(self, mock_request):
        '''Test get_seed_tray_cell: seed tray not mounted'''
        mock_response = Mock()
        mock_api_response = [{
            'id': 123,
            'name': 'Seed Tray',
            'pointer_type': '',  # not an actual data field,
        }]
        mock_response.json.return_value = mock_api_response
        mock_response.status_code = 200
        mock_response.text = 'text'
        mock_request.return_value = mock_response
        result = self.fb.get_seed_tray_cell('Seed Tray', 'a1')
        mock_request.assert_has_calls([
            call(
                method='GET',
                url='https://my.farm.bot/api/tools',
                **REQUEST_KWARGS,
            ),
            call().json(),
        ])
        self.assertIsNone(result)

    def test_get_job_one(self):
        '''Test get_job command: get one job'''
        def exec_command():
            self.fb.state.last_messages['status'] = [{
                'topic': '',
                'content': {
                    'jobs': {
                        'job name': {'status': 'working'},
                    },
                },
            }]
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
            self.fb.state.last_messages['status'] = [{
                'topic': '',
                'content': {
                    'jobs': {
                        'job name': {'status': 'working'},
                    },
                },
            }]
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
            self.fb.state.last_messages['status'] = []
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
            self.fb.if_statement(
                'Lights', 'is', 0,
                named_pin_type='Peripheral')
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
            self.fb.if_statement(
                'Lights', 'is', 0,
                named_pin_type='Peripheral')
        self.send_command_test_helper(
            exec_command,
            expected_command=None,
            extra_rpc_args={},
            mock_api_response=[{'label': 'Pump'}])
        self.assertEqual(
            self.fb.state.error,
            "ERROR: 'Lights' not in peripherals: ['Pump'].")

    def test_if_statement_with_sequences(self):
        '''Test if_statement command with sequences'''
        def exec_command():
            self.fb.if_statement(
                'pin10', '<', 0,
                'Watering Sequence',
                'Drying Sequence')
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
            self.fb.if_statement(
                'pin10', '<', 0,
                'Watering Sequence',
                'Drying Sequence')
        self.send_command_test_helper(
            exec_command,
            expected_command=None,
            extra_rpc_args={},
            mock_api_response=[])
        self.assertEqual(
            self.fb.state.error,
            "ERROR: 'Watering Sequence' not in sequences: [].")

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
            self.assertEqual(
                self.fb.state.error,
                'RPC error response received.')
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
            self.fb.state.last_messages['from_device'] = []
            self.fb.wait(100)
            self.assertEqual(
                self.fb.state.error,
                'Timed out waiting for RPC response.')
        self.send_command_test_helper(
            exec_command,
            expected_command={
                'kind': 'wait',
                'args': {'milliseconds': 100}},
            extra_rpc_args={},
            mock_api_response=[])

    def test_set_verbosity(self):
        '''Test set_verbosity.'''
        self.assertEqual(self.fb.state.verbosity, 0)
        self.fb.set_verbosity(1)
        self.assertEqual(self.fb.state.verbosity, 1)

    def test_set_timeout(self):
        '''Test set_timeout.'''
        self.assertEqual(self.fb.state.timeout['listen'], 0)
        self.fb.set_timeout(15)
        self.assertEqual(self.fb.state.timeout['listen'], 15)

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
