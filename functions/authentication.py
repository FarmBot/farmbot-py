"""
Authentication class.
"""

# └── functions/authentication.py
#     ├── [API] get_token()
#     ├── [API] check_token()
#     ├── [API] request_handling()
#     └── [API] request()

import json
import requests

class Authentication():
    """Authentication class for FarmBot API."""
    def __init__(self, state):
        self.state = state

    def get_token(self, email, password, server="https://my.farm.bot"):
        """Get FarmBot authorization token. Server is 'https://my.farm.bot' by default."""

        try:
            headers = {'content-type': 'application/json'}
            user = {'user': {'email': email, 'password': password}}
            response = requests.post(f'{server}/api/tokens', headers=headers, json=user)
            # Handle HTTP status codes
            if response.status_code == 200:
                self.state.token = response.json()
                self.state.error = None
                self.state.print_status(description=f"Successfully fetched token from {server}.")
                return response.json()
            elif response.status_code == 404:
                self.state.error = "HTTP ERROR: The server address does not exist."
            elif response.status_code == 422:
                self.state.error = "HTTP ERROR: Incorrect email address or password."
            else:
                self.state.error = f"HTTP ERROR: Unexpected status code {response.status_code}"
        # Handle DNS resolution errors
        except requests.exceptions.RequestException as e:
            if isinstance(e, requests.exceptions.ConnectionError):
                self.state.error = "DNS ERROR: The server address does not exist."
            elif isinstance(e, requests.exceptions.Timeout):
                self.state.error = "DNS ERROR: The request timed out."
            elif isinstance(e, requests.exceptions.RequestException):
                self.state.error = "DNS ERROR: There was a problem with the request."
        except Exception as e:
            self.state.error = f"DNS ERROR: An unexpected error occurred: {str(e)}"

        self.state.token = None
        self.state.print_status(description=self.state.error)
        return self.state.error

    def request_handling(self, response):
        """Handle errors associated with different endpoint errors."""

        error_messages = {
            404: "The specified endpoint does not exist.",
            400: "The specified ID is invalid or you do not have access to it.",
            401: "The user`s token has expired or is invalid.",
            502: "Please check your internet connection and try again."
        }

        # Handle HTTP status codes
        if response.status_code == 200:
            self.state.print_status(description="Successfully sent request via API.")
            return 200
        if 400 <= response.status_code < 500:
            self.state.error = json.dumps(f"CLIENT ERROR {response.status_code}: {error_messages.get(response.status_code, response.reason)}", indent=2)
        elif 500 <= response.status_code < 600:
            self.state.error = json.dumps(f"SERVER ERROR {response.status_code}: {response.text}", indent=2)
        else:
            self.state.error = json.dumps(f"UNEXPECTED ERROR {response.status_code}: {response.text}", indent=2)

        self.state.print_status(description=self.state.error)
        return response.status_code

    def request(self, method, endpoint, database_id, payload=None):
        """Make requests to API endpoints using different methods."""

        self.state.check_token()

        # use 'GET' method to view endpoint data
        # use 'POST' method to overwrite/create new endpoint data
        # use 'PATCH' method to edit endpoint data (used for new logs)
        # use 'DELETE' method to delete endpoint data (hidden)

        token = self.state.token["token"]
        iss = token["unencoded"]["iss"]

        id_part = "" if database_id is None else f"/{database_id}"
        url = f'https:{iss}/api/{endpoint}{id_part}'

        headers = {'authorization': token['encoded'], 'content-type': 'application/json'}
        response = requests.request(method, url, headers=headers, json=payload)

        if self.request_handling(response) == 200:
            self.state.error = None
            self.state.print_status(description="Successfully returned request contents.")
            return response.json()
        self.state.print_status(description="There was an error processing the request...")
        return self.state.error
