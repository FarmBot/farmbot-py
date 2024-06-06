import json
import requests
from getpass import getpass # required for authorization token
import paho.mqtt.publish as publish # required for message broker

RPC_REQUEST = {
    "kind": "rpc_request",
    "args": {
        "label": ""
    }
}

def get_token(EMAIL, PASSWORD, SERVER='https://my.farm.bot'):
    headers = {'content-type': 'application/json'}
    user = {'user': {'email': EMAIL, 'password': PASSWORD}}
    response = requests.post(f'{SERVER}/api/tokens', headers=headers, json=user)
    return response.json()

def publish_single(PAYLOAD, TOKEN):
    publish.single(
        f'bot/{TOKEN['token']['unencoded']['bot']}/from_clients',
        payload=json.dumps(PAYLOAD),
        hostname=TOKEN['token']['unencoded']['mqtt'],
        auth={
            'username': TOKEN['token']['unencoded']['bot'],
            'password': TOKEN['token']['encoded']
        }
    )

def e_stop(TOKEN):
    e_stop_message = {
        **RPC_REQUEST,
        "body": [{
            "kind": "emergency_lock",
            "args": {}
        }]
    }

    publish_single(e_stop_message, TOKEN)

def unlock(TOKEN):
    unlock_message = {
        **RPC_REQUEST,
        "body": [{
            "kind": "emergency_unlock",
            "args": {}
        }]
    }

    publish_single(unlock_message, TOKEN)

def get_info(TOKEN, SOURCE, ID=''):
    url = f'https:{TOKEN['token']['unencoded']['iss']}/api/'+SOURCE+'/'+ID
    headers = {'authorization': TOKEN['token']['encoded'], 'content-type': 'application/json'}
    response = requests.get(url, headers=headers)
    return json.dumps(response.json(), indent=2)

def edit_info(TOKEN, SOURCE, VALUE, CHANGE, ID=''):
    new_value = {
        VALUE: CHANGE
    }

    url = f'https:{TOKEN['token']['unencoded']['iss']}/api/'+SOURCE+'/'+ID
    headers = {'authorization': TOKEN['token']['encoded'], 'content-type': 'application/json'}
    response = requests.patch(url, headers=headers, data=json.dumps(new_value))
    return json.dumps(response.json(), indent=2)

def new_log_API(MESSAGE, CHANNEL, TYPE, VERBOSITY, TOKEN):
    new_message = {
        'message': MESSAGE,
        'channel': [CHANNEL], # Doesn't currently do anything
        'type': TYPE,
        'verbosity': VERBOSITY
    }

    url = f'https:{TOKEN['token']['unencoded']['iss']}/api/logs'
    headers = {'authorization': TOKEN['token']['encoded'], 'content-type': 'application/json'}
    response = requests.post(url, headers=headers, data=json.dumps(new_message))
    return json.dumps(response.json(), indent=2)

def new_log_BROKER(MESSAGE, TYPE, TOKEN):
    new_message = {
        **RPC_REQUEST,
        "body": [{
            'kind': 'send_message',
            'args': {
                'message': MESSAGE,
                'message_type': TYPE
            }
        }]
    }

    publish_single(new_message, TOKEN)

def move_to(X, Y, Z, TOKEN):
    def axis_overwrite(AXIS, VALUE):
        return {
            "kind": "axis_overwrite",
            "args": {
                "axis": AXIS,
                "axis_operand": {
                    "kind": "numeric",
                    "args": {
                        "number": VALUE
                    }
                }
            }
        }

    coordinates = {
        **RPC_REQUEST,
        "body": [{
            "kind": "move",
            "args": {},
            "body": [
                axis_overwrite("x", X),
                axis_overwrite("y", Y),
                axis_overwrite("z", Z)
            ]
        }]
    }

    publish_single(coordinates, TOKEN)

def control_peripheral(TOKEN, ID, VALUE, TYPE):
    control_message = {
        **RPC_REQUEST,
        "body": [{
            "kind": "write_pin",
            "args": {
                "pin_value": VALUE, # Controls on/off or slider value
                "pin_mode": TYPE, # Controls digital or analog
                "pin_number": {
                    "kind": "named_pin",
                    "args": {
                        "pin_type": "Peripheral",
                        "pin_id": ID
                    }
                }
            }
        }]
    }

    publish_single(control_message, TOKEN)