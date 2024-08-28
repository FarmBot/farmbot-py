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

    def calibrate_camera(self):
        """Performs camera calibration. This action will reset camera calibration settings."""

        self.broker.state.print_status(description="Triggered camera calibration")

        calibrate_message = {
            "kind": "execute_script",
            "args": {
                "label": "camera-calibration"
            },
        }

        self.broker.publish(calibrate_message)

    def take_photo(self):
        """Takes photo using the device camera and uploads it to the web app."""

        self.broker.state.print_status(description="Took a photo")

        photo_message = {
            "kind": "take_photo",
            "args": {}
        }

        self.broker.publish(photo_message)

    # TODO: photo_grid()
