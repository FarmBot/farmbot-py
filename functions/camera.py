"""
Camera class.
"""

# └── functions/camera.py
#     ├── [BROKER] calibrate_camera()
#     ├── [BROKER] take_photo()
#     └── [BROKER] photo_grid()

from .imports import *
from .broker import BrokerConnect

class Camera():
    def __init__(self, state):
        self.broker = BrokerConnect(state)

    def calibrate_camera(self):
        verbosity_level = {
            1: lambda: print("`calibrate_camera` called"),
            2: lambda: print(f"Triggered camera calibration at: {datetime.now()}")
        }

        verbosity_level[self.broker.state.verbosity]()

        calibrate_message = {
            **RPC_REQUEST,
            "body": [{
                "kind": "execute_script",
                "args": {
                    "label": "camera-calibration"
                },
            }]
        }

        self.broker.publish(calibrate_message)

    def take_photo(self):
        verbosity_level = {
            1: lambda: print("`take_photo` called"),
            2: lambda: print(f"Took a photo at: {datetime.now()}")
        }

        verbosity_level[self.broker.state.verbosity]()

        photo_message = {
            **RPC_REQUEST,
            "body": [{
                "kind": "take_photo",
                "args": {}
            }]
        }

        self.broker.publish(photo_message)

    # TODO: photo_grid()
