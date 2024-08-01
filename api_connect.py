import sys
import json
import requests

class ApiConnect():
    def __init__(self):
        self.token = None
        self.error = None

    ## ERROR HANDLING

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

    ## FUNCTIONS

    def get_token(self, email, password, server):
        """Fetch user authentication token via API."""

        try:
            headers = {'content-type': 'application/json'}
            user = {'user': {'email': email, 'password': password}}
            response = requests.post(f'{server}/api/tokens', headers=headers, json=user)
            # Handle HTTP status codes
            if response.status_code == 200:
                token_data = response.json()
                self.token = token_data # TODO
                self.error = None
                return token_data
            elif response.status_code == 404:
                self.error = "HTTP ERROR: The server address does not exist."
            elif response.status_code == 422:
                self.error = "HTTP ERROR: Incorrect email address or password."
            else:
                self.error = f"HTTP ERROR: Unexpected status code {response.status_code}"
        # Handle DNS resolution errors
        except requests.exceptions.RequestException as e:
            if isinstance(e, requests.exceptions.ConnectionError):
                self.error = "DNS ERROR: The server address does not exist."
            elif isinstance(e, requests.exceptions.Timeout):
                self.error = "DNS ERROR: The request timed out."
            elif isinstance(e, requests.exceptions.RequestException):
                self.error = "DNS ERROR: There was a problem with the request."
        except Exception as e:
            self.error = f"DNS ERROR: An unexpected error occurred: {str(e)}"

        self.token = None
        return

    def check_token(self):
        """Ensure user authentication token has been generated and persists."""

        if self.token is None:
            print("ERROR: You have no token, please call `get_token` using your login credentials and the server you wish to connect to.")
            sys.exit(1)

    def request(self, method, endpoint, database_id, payload=None):
        """Send requests to the API using various methods."""

        self.check_token()

        # use 'GET' method to view endpoint data
        # use 'POST' method to overwrite/create new endpoint data
        # use 'PATCH' method to edit endpoint data (used for new logs)
        # use 'DELETE' method to delete endpoint data (hidden)

        if database_id is None:
            url = f'https:{self.token["token"]["unencoded"]["iss"]}/api/{endpoint}'
        else:
            url = f'https:{self.token["token"]["unencoded"]["iss"]}/api/{endpoint}/{database_id}'

        headers = {'authorization': self.token['token']['encoded'], 'content-type': 'application/json'}
        response = requests.request(method, url, headers=headers, json=payload)

        if self.request_handling(response) == 200:
            self.error = None
            request_data = response.json()
            return request_data
        else:
            return self.error
