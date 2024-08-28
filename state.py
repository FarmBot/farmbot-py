"""State management."""

import json

class State():
    """State class."""
    def __init__(self):
        self.token = None
        self.error = None
        self.last_message = None
        self.verbosity = 2

    def print_status(self, function, endpoint_json=None, description=None):
        """Handle changes to output based on user-defined verbosity."""

        if self.verbosity >= 1:
            print(f"`{function}` called")
        if self.verbosity >= 2 and description:
            print(description)
        if self.verbosity >= 2 and endpoint_json:
            print(json.dumps(endpoint_json, indent=4))
