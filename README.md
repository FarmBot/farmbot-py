# sidecar-starter-pack

Authentication and communication utilities for FarmBot sidecars

[![Test Status](https://github.com/FarmBot-Labs/sidecar-starter-pack/actions/workflows/test.yml/badge.svg?branch=main)](https://github.com/FarmBot-Labs/sidecar-starter-pack/actions?query=branch%3Amain)
[![Coverage Status](https://coveralls.io/repos/github/FarmBot-Labs/sidecar-starter-pack/badge.svg?branch=main)](https://coveralls.io/github/FarmBot-Labs/sidecar-starter-pack?branch=main)

## :book: Contents

* [Installation](#computer-installation-mac-os)
* [Getting Started](#seedling-getting-started)
    * [Get your authentication token](#get-your-authentication-token)
    * [Configure function output verbosity](#configure-function-output-verbosity)
* [Functions](#compass-functions)
    * [authentication.py](#authenticationpy)
    * [basic_commands.py](#basic_commandspy)
    * [broker.py](#brokerpy)
    * [camera.py](#camerapy)
    * [information.py](#informationpy)
    * [jobs.py](#jobspy)
    * [messages.py](#messagespy)
    * [movements.py](#movementspy)
    * [peripherals.py](#peripheralspy)
    * [resources.py](#resourcespy)
    * [tools.py](#toolspy)
* [Developer Info](#toolbox-developer-info)
    * [Formatting message broker messages](#formatting-message-broker-messages)

## :computer: Installation (Mac OS)

To set up the project locally, follow these steps:

(1) Clone the repository.
```
git clone https://github.com/FarmBot-Labs/sidecar-starter-pack
```

(2) Navigate to the project directory.
```
cd path/to/sidecar-starter-pack
```

(3) Create a virtual environment.
```
python -m venv path/to/venv/location
```

(4) Activate the virtual environment.
```
source path/to/venv/bin/activate
```

(5) Install the required libraries within venv:
```
python3 -m pip install requests
python3 -m pip install paho-mqtt
```

## :seedling: Getting Started

Import `main.py` and create an instance of the Farmbot class:
```
from main.py import Farmbot
bot = Farmbot()
```

### Get your authentication token

Use the same login credentials associated with the web app account you are interacting with. The server is "https://my.farm.bot" by default.
```
bot.get_token("email", "password")
```

### Configure function output verbosity

Set the level of verbosity of function outputs to change the level of information shown when functions are called.
```
bot.set_verbosity(2)
```

| Verbosity | Example using `e_stop()` |
| :--- | :--- |
| `0` The function will return with no output. | No output. |
| `1` The name of the function will be output. | `e_stop called` |
| `2` The name of the function will be output with additional information about the return value. | `Triggered device emergency stop at: 2024-08-21 11:16:18.547813` |

### Test 1: Add a new plant to your garden

This test will help familiarize you with sending commands via the [API](https://developer.farm.bot/docs/web-app/rest-api).
```
new_cabbage = {
    "name": "Cabbage",              # Point name
    "pointer_type": "Plant",        # Point type
    "x": 400,                       # x-coordinate
    "y": 300,                       # y-coordinate
    "z": 0,                         # z-coordinate
    "openfarm_slug": "cabbage",     # Plant type
    "plant_stage": "planned",       # Point status
}

bot.add_info("points", new_cabbage) # Add plant to endpoint
```

### Test 2: Turn your LED strip on and off

This test will help familiarize you with sending commands via the [Message Broker](https://developer.farm.bot/docs/message-broker).
```
bot.on(7)           # Turn ON pin 7 (LED strip)
bot.wait(2000)      # Wait 2000 milliseconds
bot.off(7)          # Turn OFF pin 7 (LED strip)
```

## :compass: Functions

```
sidecar-starter-pack/
├── functions/
│   ├── __init_.py
│   ├── authentication.py
│   ├── basic_commands.py
│   ├── broker.py
│   ├── camera.py
│   ├── imports.py
│   ├── information.py
│   ├── jobs.py
│   ├── messages.py
│   ├── movements.py
│   ├── peripherals.py
│   ├── resources.py
│   └── tools.py
├── tests/
│   ├── __init_.py
│   └── tests_main.py
├── __init_.py
├── imports.py
├── main.py
└── README.md
```

### authentication.py

> [!CAUTION]
> Store your authorization token securely. It grants full access and control over your FarmBot and your FarmBot Web App account.

| class `Authentication()` | Description |
| :--- | :--- |
| `get_token()` | Get FarmBot authorization token. Server is "https://my.farm.bot" by default. |
| `check_token()` | Ensure the token persists throughout sidecar. |
| `request_handling()` | Handle errors associated with different endpoint errors. |
| `request()` | Make requests to API endpoints using different methods. |

### basic_commands.py

| class `BasicCommands()` | Description |
| :--- | :--- |
| `wait()` | Pauses execution for a certain number of milliseconds. |
| `e_stop()` | Emergency locks (E-stops) the Farmduino microcontroller and resets peripheral pins to OFF. |
| `unlock()` | Unlocks a locked (E-stopped) device. |
| `reboot()` | Reboots the FarmBot OS and reinitializes the device. |
| `shutdown()` | Shuts down the FarmBot OS, turning the device off. |

### broker.py

| class `BrokerConnect()` | Description |
| :--- | :--- |
| `connect()` | Establish persistent connection to send messages via message broker. |
| `disconnect()` | Disconnect from the message broker. |
| `publish()` | Publish messages containing CeleryScript via the message broker. |
| `on_connect()` | Callback function triggered when a connection to the message broker is successfully established. |
| `on_message()` | Callback function triggered when a message is received from the message broker. |
| `start_listen()` | Establish persistent subscription to message broker channels. |
| `stop_listen()` | End subscription to all message broker channels. |

### camera.py

| class `Camera()` | Description |
| :--- | :--- |
| `calibrate_camera()` | Performs camera calibration. This action will reset camera calibration settings. |
| `take_photo()` | Takes a photo using the device camera and uploads it to the web app. |
<!--- | `photo_grid()` | Returns metadata object about point grid required to perform a scan of the full garden. | --->

### information.py

> [!CAUTION]
> Making requests other than `GET` to the API will permanently alter the data in your account. `DELETE` and `POST` requests may destroy data that cannot be recovered. Altering data through the API may cause account instability.

> [!NOTE]
> Not sure which endpoint to access? [Find the list here](https://developer.farm.bot/docs/web-app/api-docs).

| class `Information()` | Description |
| :--- | :--- |
| `get_info()` | Get information about a specific endpoint. |
| `set_info()` | Change information contained within an endpoint. |
| `safe_z()` | Returns the highest safe point along the z-axis. |
| `garden_size()` | Returns x-axis length, y-axis length, and area of garden bed. |
| `group()` | Returns all group info or single by id. |
| `curve()` | Returns all curve info or single by id. |
| `soil_height()` | Use the camera to determine soil height at the current location. |
| `read_status()` | Returns the FarmBot status tree. |
| `read_sensor()` | Reads the given pin by id. |

### jobs.py

| class `JobHandling()` | Description |
| :--- | :--- |
| `get_job()` | Retrieves the status or details of the specified job. |
| `set_job()` | Initiates or modifies job with given parameters. |
| `complete_job()` | Marks job as completed and triggers any associated actions. |

### messages.py

| class `MessageHandling()` | Description |
| :--- | :--- |
| `log()` | Sends new log message via the API. Requires the page to be refreshed before appearing. |
| `message()` | Sends new log message via the message broker. |
| `debug()` | Sends debug message used for developer information or troubleshooting. |
| `toast()` | Sends a message that pops up on the user interface briefly. |

### movements.py

| class `MovementControls()` | Description |
| :--- | :--- |
| `move()` | Moves to the specified (x, y, z) coordinate. |
| `set_home()` | Sets the current position as the home position for a specific axis. |
| `find_home()` | Moves the device to the home position for a specified axis. |
| `axis_length()` | Returns the length of a specified axis. |
| `get_xyz()` | Returns the current (x, y, z) coordinates of the FarmBot. |
| `check_position()` | Verifies position of the FarmBot within specified tolerance range. |

### peripherals.py

| class `Peripherals()` | Description |
| :--- | :--- |
| `control_servo()` | Set servo angle between 0-100 degrees. |
| `control_peripheral()` | Set peripheral value (ON/OFF or slider value from 0-255) and mode (digital or analog). |
| `toggle_peripheral()` | Toggles the state of a specific peripheral between 'on' (100%) and 'off' (0%). |
| `on()` | Turns specified peripheral 'on' (100%). |
| `off()` | Turns specified peripheral 'off' (0%). |

### resources.py

| class `Resources()` | Description |
| :--- | :--- |
| `mark_coord()` | Marks (x, y, z) coordinate with specified label. |
| `sequence()` | Executes a predefined sequence. |
| `get_seed_tray_cell()` | Identifies and returns the location of specified cell in the seed tray. |
| `detect_weeds()` | Scans the garden to detect weeds. |
| `lua()` | Executes custom Lua code snippets to perform complex tasks or automations. |
| `if_statement()` | Performs conditional check and executes actions based on the outcome. |
| `assertion()` | Evaluates an expression. |
<!--- | `sort_points()` | Sorts list of points (e.g., plants, weeds) based on specified criteria. | --->

### tools.py

| class `ToolControls()` | Description |
| :--- | :--- |
| `mount_tool()` | Mounts the given tool and pulls it out of assigned slot. |
| `dismount_tool()` | Dismounts the currently mounted tool into assigned slot. |
| `water()` | Moves to and waters plant based on age and assigned watering curve. |
| `dispense()` | Dispenses user-defined amount of liquid in milliliters. |
<!--- | `verify_tool()` | Verifies if tool is mounted to UTM via tool verification pin and MOUNTED TOOL field in FarmBot’s state tree. | --->

## :toolbox: Developer Info

### Formatting message broker messages

> [!NOTE]
> Messages sent via the message broker contain [CeleryScript nodes](https://developer.farm.bot/docs/celery-script/nodes.html) which require special formatting.

```
message = {
    "kind": "rpc_request",
    "args": {
        "label": # node,
        "priority": # number
    },
    "body": [
        {
            # instructions
        }
    ]
}
```
