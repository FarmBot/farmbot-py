"""
Camera class.
"""

# └── functions/camera.py
#     ├── [BROKER] calibrate_camera()
#     ├── [BROKER] take_photo()
#     └── [BROKER] photo_grid()

from datetime import datetime
from .broker import BrokerConnect

RPC_REQUEST = {
    "kind": "rpc_request",
    "args": {
        "label": "",
    }
}

class Camera():
    def __init__(self, state):
        self.broker = BrokerConnect(state)

    def calibrate_camera(self):
        """Performs camera calibration. This action will reset camera calibration settings."""

        self.broker.state.print_status(description=f"Triggered camera calibration at: {datetime.now()}")

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
        return

    def take_photo(self):
        """Takes photo using the device camera and uploads it to the web app."""

        self.broker.state.print_status(description=f"Took a photo at: {datetime.now()}")

        photo_message = {
            **RPC_REQUEST,
            "body": [{
                "kind": "take_photo",
                "args": {}
            }]
        }

        self.broker.publish(photo_message)
        return

    # TODO: photo_grid()
