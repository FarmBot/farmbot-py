import sys
import os
import json
import requests

class ApiFunctions():
    def __init__(self):
        self.token = None
        self.error = None

    # token_handling() --> errors for token
    # request_handling() --> errors for request

    # get_token()
    # check_token()

    # request()
    # get() --> get endpoint info
    # post() --> overwrite/new endpoint info
    # patch() --> edit endpoint info
    # delete() --> delete endpoint info

    def token_handling(self, response):
        # Handle HTTP status codes
        if response.status_code == 200:
            return 200
        elif response.status_code == 404:
            self.error = "ERROR: The server address does not exist."
        elif response.status_code == 422:
            self.error = "ERROR: Incorrect email address or password."
        else:
            self.error = f"ERROR: Unexpected status code {response.status_code}"

        # Handle DNS resolution errors
        if response is None:
            self.error = "ERROR: There was a problem with the request."
        elif isinstance(response, requests.exceptions.ConnectionError):
            self.error = "ERROR: The server address does not exist."
        elif isinstance(response, requests.exceptions.Timeout):
            self.error = "ERROR: The request timed out."
        elif isinstance(response, requests.exceptions.RequestException):
            self.error = "ERROR: There was a problem with the request."

        return 0

    def request_handling(self, response):
        error_messages = {
            404: "The specified endpoint does not exist.",
            400: "The specified ID is invalid or you do not have access to it.",
            401: "The user`s token has expired or is invalid.",
            502: "Please check your internet connection and try again."
        }

        # Handle HTTP status codes
        if response.status_code == 200:
            return 200
        elif 400 <= response.status_code < 500:
            self.error = json.dumps(f"CLIENT ERROR {response.status_code}: {error_messages.get(response.status_code, response.reason)}", indent=2)
        elif 500 <= response.status_code < 600:
            self.error = json.dumps(f"SERVER ERROR {response.status_code}: {response.text}", indent=2)
        else:
            self.error = json.dumps(f"UNEXPECTED ERROR {response.status_code}: {response.text}", indent=2)

        return 0

    def get_token(self, email, password, server):
        headers = {'content-type': 'application/json'}
        user = {'user': {'email': email, 'password': password}}
        response = requests.post(f'{server}/api/tokens', headers=headers, json=user)

        if self.token_handling(response) == 200:
            self.token = response.json()
            self.error = None
            return self.token
        else:
            return self.error

    def check_token(self):
        if self.token is None:
            print("ERROR: You have no token, please call `get_token` using your login credentials and the server you wish to connect to.")
            sys.exit(1)

    def request(self, method, endpoint, id, payload):
        self.check_token()

        if id is None:
            url = f'https:{self.token["token"]["unencoded"]["iss"]}/api/{endpoint}'
        else:
            url = f'https:{self.token["token"]["unencoded"]["iss"]}/api/{endpoint}/{id}'

        headers = {'authorization': self.token['token']['encoded'], 'content-type': 'application/json'}
        response = requests.request(method, url, headers=headers, json=payload)

        if self.request_handling(response) == 200:
            user_request = response.json()
            self.error = None
            return user_request
        else:
            return self.error

    def get(self, endpoint, id):
        return self.request('GET', endpoint, id, payload=None)

    def post(self, endpoint, id, payload):
        return self.request('POST', endpoint, id, payload)

    def patch(self, endpoint, id, payload):
        return self.request('PATCH', endpoint, id, payload)

    def delete(self, endpoint, id):
        return self.request('DELETE', endpoint, id, payload=None)
