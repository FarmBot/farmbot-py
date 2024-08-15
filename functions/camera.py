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
        # Execute calibrate camera script
        # No inherent return value
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
        # Take single photo
        # No inherent return value
        take_photo_message = {
            **RPC_REQUEST,
            "body": [{
                "kind": "take_photo",
                "args": {}
            }]
        }

        self.broker.publish(take_photo_message)

    # TODO: photo_grid()
