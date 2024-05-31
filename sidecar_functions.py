import json
import requests
from getpass import getpass # required for get_token

"""
FUNCTION:       get_token
PARAMETERS:     'EMAIL' is the user's email address associated w/ web app account, passed as a string
                'PASSWORD' is the user's password associated w/ web app account, passed as a string
"""

def get_token(EMAIL, PASSWORD):
    headers = {'content-type': 'application/json'}
    user = {'user': {'email': EMAIL, 'password': PASSWORD}}
    response = requests.post(f'{'https://my.farm.bot'}/api/tokens', headers=headers, json=user)
    return response.json()

# get_token('email', 'password')

"""
FUNCTION:       get_info
PARAMETERS:     'SOURCE' may be 'device', 'logs', 'peripherals', etc..., passed as a string
                'TOKEN' is the user's auth token saved as a variable, passed as a variable
"""

def get_info(SOURCE, TOKEN):
    url = f'https:{TOKEN['token']['unencoded']['iss']}/api/'+SOURCE
    headers = {'authorization': TOKEN['token']['encoded'], 'content-type': 'application/json'}
    response = requests.get(url, headers=headers)
    return print(json.dumps(response.json(), indent=2))

# get_info('device', TOKEN)

"""
FUNCTION:       edit_info
PARAMETERS:     'SOURCE' may be 'device', 'logs', 'peripherals', etc..., passed as a string
                'VALUE' may be the field you would like to change, passed as a string
                'CHANGE' may be the new value of the field, passed as a string
                'TOKEN' is the user's auth token saved as a variable, passed as a variable
"""

def edit_info(SOURCE, VALUE, CHANGE, TOKEN):
    new_value = {
        VALUE: CHANGE
    }

    url = f'https:{TOKEN['token']['unencoded']['iss']}/api/'+SOURCE
    headers = {'authorization': TOKEN['token']['encoded'], 'content-type': 'application/json'}
   
    response = requests.patch(url, headers=headers, data=json.dumps(new_value))

    return print(json.dumps(response.json(), indent=2))

# edit_info('device', 'name', 'Orange Orangutan', TOKEN)

"""
FUNCTION:       new_log
PARAMETERS:     'MESSAGE' is the log message the user wishes to send, passed as a string
                'TOKEN' is the user's auth token saved as a variable, passed as a variable
"""

def new_log(MESSAGE, TOKEN):
    new_message = {
        'message': MESSAGE
    }

    url = f'https:{TOKEN['token']['unencoded']['iss']}/api/logs'
    headers = {'authorization': TOKEN['token']['encoded'], 'content-type': 'application/json'}
    response = requests.post(url, headers=headers, data=json.dumps(new_message))
    return print(json.dumps(response.json(), indent=2))

# new_log('This is a new log message', TOKEN)