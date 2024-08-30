"""
ApiConnect class.
"""

# └── functions/api.py
#     ├── [API] get_token()
#     ├── [API] check_token()
#     ├── [API] request_handling()
#     └── [API] request()

import json
from html.parser import HTMLParser
import requests


class HTMLResponseParser(HTMLParser):
    """Response parser for HTML content."""
    def __init__(self):
        super().__init__()
        self.is_header = False
        self.headers = []

    def read(self, data):
        """Read the headers from the HTML content."""
        self.is_header = False
        self.headers = []
        self.reset()
        self.feed(data)
        return " ".join(self.headers)

    def handle_starttag(self, tag, attrs):
        """Detect headers."""
        if tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            self.is_header = True

    def handle_data(self, data):
        """Add header data to the list."""
        if self.is_header:
            self.headers.append(data.strip())
            self.is_header = False


class ApiConnect():
    """Connect class for FarmBot API."""
    def __init__(self, state):
        self.state = state

    def get_token(self, email, password, server="https://my.farm.bot"):
        """Get FarmBot authorization token. Server is 'https://my.farm.bot' by default."""
        self.state.ssl = "https" in server
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

    @staticmethod
    def parse_text(text):
        """Parse response text."""
        if '<html' in text:
            parser = HTMLResponseParser()
            return parser.read(text)
        return text

    def request_handling(self, response, make_request):
        """Handle errors associated with different endpoint errors."""

        error_messages = {
            404: "The specified endpoint does not exist.",
            400: "The specified ID is invalid or you do not have access to it.",
            401: "The user`s token has expired or is invalid.",
            502: "Please check your internet connection and try again."
        }

        text = self.parse_text(response.text)

        # Handle HTTP status codes
        if response.status_code == 200:
            if not make_request:
                description = "Editing disabled, request not sent."
            else:
                description = "Successfully sent request via API."
            self.state.print_status(description=description)
            return 200
        if 400 <= response.status_code < 500:
            self.state.error = f"CLIENT ERROR {response.status_code}: {error_messages.get(response.status_code, response.reason)}"
        elif 500 <= response.status_code < 600:
            self.state.error = f"SERVER ERROR {response.status_code}: {text}"
        else:
            self.state.error = f"UNEXPECTED ERROR {response.status_code}: {text}"

        try:
            response.json()
        except requests.exceptions.JSONDecodeError:
                self.state.error += f" ({text})"
        else:
            self.state.error += f" ({json.dumps(response.json(), indent=2)})"

        self.state.print_status(description=self.state.error)
        return response.status_code

    def request(self, method, endpoint, database_id, payload=None):
        """Make requests to API endpoints using different methods."""

        self.state.check_token()

        # use 'GET' method to view endpoint data
        # use 'POST' method to overwrite/create new endpoint data
        # use 'PATCH' method to edit endpoint data (used for new logs)
        # use 'DELETE' method to delete endpoint data

        token = self.state.token["token"]
        iss = token["unencoded"]["iss"]

        id_part = "" if database_id is None else f"/{database_id}"
        http_part = "https" if self.state.ssl else "http"
        url = f'{http_part}:{iss}/api/{endpoint}{id_part}'

        headers = {'authorization': token['encoded'], 'content-type': 'application/json'}
        make_request = not self.state.dry_run or method == "GET"
        if make_request:
            response = requests.request(method, url, headers=headers, json=payload)
        else:
            response = requests.Response()
            response.status_code = 200
            response._content = b'{"edit_requests_disabled": true}'

        if self.request_handling(response, make_request) == 200:
            self.state.error = None
            self.state.print_status(description="Successfully returned request contents.")
            return response.json()
        self.state.print_status(description="There was an error processing the request...")
        return self.state.error
