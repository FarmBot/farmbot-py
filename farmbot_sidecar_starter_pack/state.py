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
    arg_strings = [f"{arg}={repr(values[arg])}" for arg in args if arg != "self"]
    arg_str = ", ".join(arg_strings)
    return f"{func_name}({arg_str})"


class State():
    """State class."""

    NO_TOKEN_ERROR = "ERROR: You have no token, please call `get_token` using your login credentials and the server you wish to connect to."

    def __init__(self):
        self.token = None
        self.error = None
        self.last_messages = {}
        self.last_published = {}
        self.verbosity = 2
        self.broker_listen_duration = 15
        self.test_env = False
        self.ssl = True
        self.min_call_stack_depth = 100
        self.dry_run = False

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
                print(indent + description, end=end, flush=(end == ""))
            if endpoint_json:
                json_str = json.dumps(endpoint_json, indent=4)
                indented_str = indent + json_str.replace("\n", "\n" + indent)
                print(indented_str)

    def check_token(self):
        """Ensure the token persists throughout sidecar."""

        if self.token is None:
            self.print_status(description=self.NO_TOKEN_ERROR)
            self.error = self.NO_TOKEN_ERROR
            raise ValueError(self.NO_TOKEN_ERROR)
