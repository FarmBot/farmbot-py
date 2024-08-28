"""State management."""

import json
import inspect
from datetime import datetime

def get_function_call_info():
    """Return the name and given arguments of the function where this is called."""
    # back to print_status then back to the function that called print_status
    frame = inspect.currentframe().f_back.f_back
    func_name = frame.f_code.co_name
    args, _, _, values = inspect.getargvalues(frame)
    arg_strings = [f"{arg}={repr(values[arg])}" for arg in args if arg != 'self']
    arg_str = ', '.join(arg_strings)
    return f"{func_name}({arg_str})"

class State():
    """State class."""
    def __init__(self):
        self.token = None
        self.error = None
        self.last_message = None
        self.verbosity = 2

    def print_status(self, endpoint_json=None, description=None):
        """Handle changes to output based on user-defined verbosity."""

        if self.verbosity >= 1:
            if description:
                print(description)
            if endpoint_json:
                print(json.dumps(endpoint_json, indent=4))
        if self.verbosity >= 2:
            function = get_function_call_info()
            print(f"`{function}` called at {datetime.now()}")
