# farmbot_API.py

import sys
import json
import requests

class FarmbotAPI():
    def __init__(self):
        self.token = None
        self.error = None

    def get_token(self, EMAIL, PASSWORD, SERVER):
        try:
            headers = {'content-type': 'application/json'}
            user = {'user': {'email': EMAIL, 'password': PASSWORD}}
            response = requests.post(f'{SERVER}/api/tokens', headers=headers, json=user)

            # Handle HTTP status codes
            if response.status_code == 200:
                self.token = response.json()
                self.error = None
                return json.dumps(response.json(), indent=2)
            elif response.status_code == 404:
                self.error = "ERROR: The server address does not exist."
            elif response.status_code == 422:
                self.error = "ERROR: Incorrect email address or password."
            else:
                self.error = f"ERROR: Unexpected status code {response.status_code}"

        # Handle DNS resolution errors
        except requests.exceptions.RequestException as e:
            if isinstance(e, requests.exceptions.ConnectionError):
                self.error = "ERROR: The server address does not exist."
            elif isinstance(e, requests.exceptions.Timeout):
                self.error ="ERROR: The request timed out."
            elif isinstance(e, requests.exceptions.RequestException):
                self.error = "ERROR: There was a problem with the request."
        except Exception as e:
            self.error = f"ERROR: An unexpected error occurred: {str(e)}"

        self.token = None
        return self.error

    def check_token(self):
        if self.token is None:
            print("ERROR: You have no token, please call `get_token` using your login credentials and the server you wish to connect to.")
            sys.exit(1)

    def request(self, METHOD, ENDPOINT, ID, PAYLOAD, FIELD):
        self.check_token()

        if ID == None:
            url = f'https:{self.token["token"]["unencoded"]["iss"]}/api/{ENDPOINT}'
        else:
            url = f'https:{self.token["token"]["unencoded"]["iss"]}/api/{ENDPOINT}/{ID}'

        headers = {'authorization': self.token['token']['encoded'], 'content-type': 'application/json'}
        response = requests.request(METHOD, url, headers=headers, json=PAYLOAD)

        error_messages = {
            404: "The specified endpoint does not exist.",
            400: "The specified ID is invalid or you do not have access to it.",
            401: "The user`s token has expired or is invalid.",
            502: "Please check your internet connection and try again."
        }

        if response.status_code == 200:
            if FIELD == None:
                return json.dumps(response.json(), indent=2)
            else:
                return response.json().get(FIELD)
        elif 400 <= response.status_code < 500:
            return json.dumps(f"CLIENT ERROR {response.status_code}: {error_messages.get(response.status_code, response.reason)}", indent=2)
        elif 500 <= response.status_code < 600:
            return json.dumps(f"SERVER ERROR {response.status_code}: {response.text}", indent=2)
        else:
            return json.dumps(f"UNEXPECTED ERROR {response.status_code}: {response.text}", indent=2)

    def get(self, ENDPOINT, ID, FIELD):
        return self.request('GET', ENDPOINT, ID, PAYLOAD=None, FIELD=FIELD)

    def post(self, ENDPOINT, ID, PAYLOAD):
        return self.request('POST', ENDPOINT, ID, PAYLOAD, FIELD=None)

    def patch(self, ENDPOINT, ID, PAYLOAD):
        return self.request('PATCH', ENDPOINT, ID, PAYLOAD, FIELD=None)