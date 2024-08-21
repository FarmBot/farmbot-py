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
| `get_token()` | <a href="https://developer.farm.bot/v15/docs/web-app/rest-api.html"><img src="https://img.shields.io/badge/REST%20API-FF9500"/></a> Get FarmBot authorization token. Server is "https://my.farm.bot" by default. |
| `check_token()` | <a href="https://developer.farm.bot/v15/docs/web-app/rest-api.html"><img src="https://img.shields.io/badge/REST%20API-FF9500"/></a> Ensure the token persists throughout sidecar. |
| `request_handling()` | <a href="https://developer.farm.bot/v15/docs/web-app/rest-api.html"><img src="https://img.shields.io/badge/REST%20API-FF9500"/></a> Handle errors associated with different endpoint errors. |
| `request()` | <a href="https://developer.farm.bot/v15/docs/web-app/rest-api.html"><img src="https://img.shields.io/badge/REST%20API-FF9500"/></a> Make requests to API endpoints using different methods. |

### basic_commands.py

| class `BasicCommands()` | Description |
| :--- | :--- |
| `wait()` | <a href="https://developer.farm.bot/v15/docs/message-broker"><img src="https://img.shields.io/badge/Message%20Broker-66BF34"/></a> Pauses execution for a certain number of milliseconds. |
| `e_stop()` | <a href="https://developer.farm.bot/v15/docs/message-broker"><img src="https://img.shields.io/badge/Message%20Broker-66BF34"/></a> Emergency locks (E-stops) the Farmduino microcontroller and resets peripheral pins to OFF. |
| `unlock()` | <a href="https://developer.farm.bot/v15/docs/message-broker"><img src="https://img.shields.io/badge/Message%20Broker-66BF34"/></a> Unlocks a locked (E-stopped) device. |
| `reboot()` | <a href="https://developer.farm.bot/v15/docs/message-broker"><img src="https://img.shields.io/badge/Message%20Broker-66BF34"/></a> Reboots the FarmBot OS and reinitializes the device. |
| `shutdown()` | <a href="https://developer.farm.bot/v15/docs/message-broker"><img src="https://img.shields.io/badge/Message%20Broker-66BF34"/></a> Shuts down the FarmBot OS, turning the device off. |

### broker.py

| class `BrokerConnect()` | Description |
| :--- | :--- |
| `connect()` | [BROKER] Establish persistent connection to send messages via message broker. |
| `disconnect()` | [BROKER] Disconnect from the message broker. |
| `publish()` | [BROKER] Publish messages containing CeleryScript via the message broker. |
| `on_connect()` | [BROKER] Callback function triggered when a connection to the message broker is successfully established. |
| `on_message()` | [BROKER] Callback function triggered when a message is received from the message broker. |
| `start_listen()` | [BROKER] Establish persistent subscription to message broker channels. |
| `stop_listen()` | [BROKER] End subscription to all message broker channels. |

### camera.py

| class `Camera()` | Description |
| :--- | :--- |
| `calibrate_camera()` | [BROKER] Performs camera calibration. This action will reset camera calibration settings. |
| `take_photo()` | [BROKER] Takes a photo using the device camera and uploads it to the web app. |
<!--- | `photo_grid()` | [BROKER] Returns metadata object about point grid required to perform a scan of the full garden. | --->

### information.py

> [!CAUTION]
> Making requests other than `GET` to the API will permanently alter the data in your account. `DELETE` and `POST` requests may destroy data that cannot be recovered. Altering data through the API may cause account instability.

> [!NOTE]
> Not sure which endpoint to access? [Find the list here](https://developer.farm.bot/v15/docs/web-app/api-docs).

| class `Information()` | Description |
| :--- | :--- |
| `get_info()` | [API] Get information about a specific endpoint. |
| `set_info()` | [API] Change information contained within an endpoint. |
| `safe_z()` | [API] Returns the highest safe point along the z-axis. |
| `garden_size()` | [API] Returns x-axis length, y-axis length, and area of garden bed. |
| `group()` | [API] Returns all group info or single by id. |
| `curve()` | [API] Returns all curve info or single by id. |
| `soil_height()` | [BROKER] Use the camera to determine soil height at the current location. |
| `read_status()` | [BROKER] Returns the FarmBot status tree. |
| `read_sensor()` | [BROKER] Reads the given pin by id. |

### jobs.py

| class `JobHandling()` | Description |
| :--- | :--- |
| `get_job()` | [BROKER] Retrieves the status or details of the specified job. |
| `set_job()` | [BROKER] Initiates or modifies job with given parameters. |
| `complete_job()` | [BROKER] Marks job as completed and triggers any associated actions. |

### messages.py

| class `MessageHandling()` | Description |
| :--- | :--- |
| `log()` | [API] Sends new log message via the API. Requires the page to be refreshed before appearing. |
| `message()` | [BROKER] Sends new log message via the message broker. |
| `debug()` | [BROKER] Sends debug message used for developer information or troubleshooting. |
| `toast()` | [BROKER] Sends a message that pops up on the user interface briefly. |

### movements.py

| class `MovementControls()` | Description |
| :--- | :--- |
| `move()` | [BROKER] Moves to the specified (x, y, z) coordinate. |
| `set_home()` | [BROKER] Sets the current position as the home position for a specific axis. |
| `find_home()` | [BROKER] Moves the device to the home position for a specified axis. |
| `axis_length()` | [BROKER] Returns the length of a specified axis. |
| `get_xyz()` | [BROKER] Returns the current (x, y, z) coordinates of the FarmBot. |
| `check_position()` | [BROKER] Verifies position of the FarmBot within specified tolerance range. |

### peripherals.py

| class `Peripherals()` | Description |
| :--- | :--- |
| `control_servo()` | [BROKER] Set servo angle between 0-100 degrees. |
| `control_peripheral()` | [BROKER] Set peripheral value (ON/OFF or slider value from 0-255) and mode (digital or analog). |
| `toggle_peripheral()` | [BROKER] Toggles the state of a specific peripheral between 'on' (100%) and 'off' (0%). |
| `on()` | [BROKER] Turns specified peripheral 'on' (100%). |
| `off()` | [BROKER] Turns specified peripheral 'off' (0%). |

### resources.py

| class `Resources()` | Description |
| :--- | :--- |
| `mark_coord()` | [BROKER] Marks (x, y, z) coordinate with specified label. |
| `sequence()` | [BROKER] Executes a predefined sequence. |
| `get_seed_tray_cell()` | [BROKER] Identifies and returns the location of specified cell in the seed tray. |
| `detect_weeds()` | [BROKER] Scans the garden to detect weeds. |
| `lua()` | [BROKER] Executes custom Lua code snippets to perform complex tasks or automations. |
| `if_statement()` | [BROKER] Performs conditional check and executes actions based on the outcome. |
| `assertion()` | [BROKER] Evaluates an expression. |
<!--- | `sort_points()` | [BROKER] Sorts list of points (e.g., plants, weeds) based on specified criteria. | --->

### tools.py

| class `ToolControls()` | Description |
| :--- | :--- |
| `mount_tool()` | [BROKER] Mounts the given tool and pulls it out of assigned slot. |
| `dismount_tool()` | [BROKER] Dismounts the currently mounted tool into assigned slot. |
| `water()` | [BROKER] Moves to and waters plant based on age and assigned watering curve. |
| `dispense()` | [BROKER] Dispenses user-defined amount of liquid in milliliters. |
<!--- | `verify_tool()` | [BROKER] Verifies if tool is mounted to UTM via tool verification pin and MOUNTED TOOL field in FarmBot’s state tree. | --->

## :toolbox: Developer Info

### Formatting message broker messages

> [!NOTE]
> Messages sent via the message broker contain [CeleryScript nodes](https://developer.farm.bot/v15/docs/celery-script/nodes.html) which require special formatting.

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
