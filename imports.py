"""
Imports and dependencies for main module.
"""

# Imports

from functions.authentication import Authentication
from functions.basic_commands import BasicCommands
from functions.broker import BrokerConnect
from functions.camera import Camera
from functions.information import Information
from functions.jobs import JobHandling
from functions.messages import MessageHandling
from functions.movements import MovementControls
from functions.peripherals import Peripherals
from functions.resources import Resources
from functions.tools import ToolControls

# Classes

auth = Authentication()
basic = BasicCommands()
broker = BrokerConnect()
camera = Camera()
info = Information()
job = JobHandling()
message = MessageHandling()
move = MovementControls()
peripheral = Peripherals()
resource = Resources()
tool = ToolControls()
