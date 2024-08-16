"""
Imports and dependencies for functions module.
"""

# Imports

import sys
import json
import requests

import time
import datetime
from datetime import datetime

import paho.mqtt.client as mqtt

# Definitions

RPC_REQUEST = {
    "kind": "rpc_request",
    "args": {
        "label": ""
    }
}
