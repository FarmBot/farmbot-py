"""
Camera class.
"""

# └── functions/camera.py
#     ├── [BROKER] calibrate_camera()
#     ├── [BROKER] take_photo()
#     └── [BROKER] photo_grid()

from .broker import BrokerConnect


class Camera():
    """Camera class."""

    def __init__(self, state):
        self.broker = BrokerConnect(state)
        self.state = state

    def calibrate_camera(self):
        """Performs camera calibration. This action will reset camera calibration settings."""

        self.state.print_status(description="Calibrating camera")

        calibrate_message = {
            "kind": "execute_script",
            "args": {
                "label": "camera-calibration"
            },
        }

        self.broker.publish(calibrate_message)

    def take_photo(self):
        """Takes photo using the device camera and uploads it to the web app."""

        self.state.print_status(description="Taking a photo")

        photo_message = {
            "kind": "take_photo",
            "args": {}
        }

        self.broker.publish(photo_message)

    # TODO: photo_grid()
