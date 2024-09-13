"""State management."""

import json
import inspect
from datetime import datetime


def get_call_stack_depth():
    """Return the depth of the current call stack."""
    depth = 0
    frame = inspect.currentframe()
    while frame:
        depth += 1
        frame = frame.f_back
    return depth


def get_function_call_info():
    """Return the name and given arguments of the function where this is called."""
    # back to print_status then back to the function that called print_status
    frame = inspect.currentframe().f_back.f_back
    func_name = frame.f_code.co_name
    args, _, _, values = inspect.getargvalues(frame)
    arg_strings = []
    for arg in args:
        if arg != "self":
            arg_strings.append(f"{arg}={repr(values[arg])}")
    arg_str = ", ".join(arg_strings)
    return f"{func_name}({arg_str})"


NO_TOKEN_ERROR = """
ERROR: You have no token, please call `get_token`
using your login credentials and the server you wish to connect to.
"""


class State():
    """State class."""

    NO_TOKEN_ERROR = NO_TOKEN_ERROR.replace("\n", "")

    def __init__(self):
        self.token = None
        self.error = None
        self.last_messages = {}
        self.last_published = {}
        self.verbosity = 1
        self.json_printing = True
        self.timeout = {
            "api": 15,
            "listen": 15,
            "movements": 120,
        }
        self.test_env = False
        self.ssl = True
        self.min_call_stack_depth = 100
        self.dry_run = False
        self.resource_cache = {}

    def print_status(self, endpoint_json=None, description=None, update_only=False, end="\n"):
        """Handle changes to output based on user-defined verbosity."""
        depth = get_call_stack_depth()
        if depth < self.min_call_stack_depth:
            self.min_call_stack_depth = depth
        top = depth == self.min_call_stack_depth
        no_end = end == "" and description != ""
        indent = "" if (top or no_end) else " " * 4

        if self.verbosity >= 2 and not update_only:
            if top:
                print()
            function = get_function_call_info()
            print(f"{indent}`{function}` called at {datetime.now()}")
        if self.verbosity >= 1:
            if self.verbosity == 1 and not update_only and top:
                print()
            if description is not None:
                print(indent + description, end=end, flush=end == "")
            if endpoint_json is not None and self.json_printing:
                json_str = json.dumps(endpoint_json, indent=4)
                indented_str = indent + json_str.replace("\n", "\n" + indent)
                print(indented_str)

    def check_token(self):
        """Check if a token is present."""
        if self.token is None:
            self.print_status(description=self.NO_TOKEN_ERROR)
            self.error = self.NO_TOKEN_ERROR
            raise ValueError(self.NO_TOKEN_ERROR)

    def save_cache(self, endpoint, records):
        """Cache records."""
        self.resource_cache[endpoint] = records

    def fetch_cache(self, endpoint):
        """Fetch cached records."""
        return self.resource_cache.get(endpoint)

    def clear_cache(self, endpoint=None):
        """Clear the cache."""
        if endpoint is not None and endpoint in self.resource_cache:
            del self.resource_cache[endpoint]
        else:
            self.resource_cache = {}
