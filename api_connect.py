import sys
import json
import requests

class ApiConnect():
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
        """Handle errors relating to bad user auth token requests."""

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
        """Handle errors relating to bad endpoints and user requests."""

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
        """Fetch user authentication token via API."""

        headers = {'content-type': 'application/json'}
        user = {'user': {'email': email, 'password': password}}
        response = requests.post(f'{server}/api/tokens', headers=headers, json=user)

        if self.token_handling(response) == 200:
            user_data = response.json()
            user_token = user_data['token']
            self.error = None
            return user_token
        else:
            return self.error

    def check_token(self):
        """Ensure user authentication token has been generated and persists."""

        if self.token is None:
            print("ERROR: You have no token, please call `get_token` using your login credentials and the server you wish to connect to.")
            sys.exit(1)

    def request(self, method, endpoint, id, payload):
        """Send requests from user-accessible functions via API."""

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
        """METHOD: 'get' allows user to view endpoint data."""
        return self.request('GET', endpoint, id, payload=None)

    def post(self, endpoint, id, payload):
        """METHOD: 'post' allows user to overwrite/create new endpoint data."""
        return self.request('POST', endpoint, id, payload)

    def patch(self, endpoint, id, payload):
        """METHOD: 'patch' allows user to edit endpoint data (used for new logs)."""
        return self.request('PATCH', endpoint, id, payload)

    def delete(self, endpoint, id):
        """METHOD: 'delete' allows user to delete endpoint data (hidden)."""
        return self.request('DELETE', endpoint, id, payload=None)
