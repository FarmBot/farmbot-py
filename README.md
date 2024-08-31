# sidecar-starter-pack

This library provides authentication, API, and control utilities for **FarmBot sidecars**. A **sidecar** is another computer such as a Raspberry Pi, laptop, or server that you are in full control of to install your own packages onto and run your own code, unlocking what cannot be done using FarmBot OS or the web app alone. For example, a sidecar could:

- Extend the capabilities of your FarmBot with specialized hardware such as a GPU, or a camera or other sensor requiring special drivers.
- Expose your FarmBot's hardware capabilities as a device in a larger ecosystem such as one for home automation or scientific research.
- Perform more advanced manipulation of your web app account's data which may be infeasible using the frontend interface.

[![Test Status](https://github.com/FarmBot-Labs/sidecar-starter-pack/actions/workflows/test.yml/badge.svg?branch=main)](https://github.com/FarmBot-Labs/sidecar-starter-pack/actions?query=branch%3Amain)
[![Coverage Status](https://coveralls.io/repos/github/FarmBot-Labs/sidecar-starter-pack/badge.svg?branch=main)](https://coveralls.io/github/FarmBot-Labs/sidecar-starter-pack?branch=main)
[![PyPI - Version](https://img.shields.io/pypi/v/farmbot-sidecar-starter-pack)](https://pypi.org/project/farmbot-sidecar-starter-pack/)

## :book: Contents

* [Installation](#computer-installation-mac-os)
* [Getting Started](#seedling-getting-started)
    * [Get your authentication token](#get-your-authentication-token)
    * [Configure function output verbosity](#configure-function-output-verbosity)
* [Functions](#compass-functions)
    * [api.py](#api)
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

## :computer: Installation

To use the sidecar starter pack, follow these steps:

(1) Create a virtual environment.
```bash
python -m venv py_venv
```

(2) Activate the virtual environment.
```bash
source py_venv/bin/activate
```

(3) Install the farmbot-sidecar-starter-pack library within the virtual environment:
```bash
python -m pip install farmbot-sidecar-starter-pack
```

## :seedling: Getting Started

Import `farmbot_sidecar_starter_pack` and create an instance of the Farmbot class:
```python
from farmbot_sidecar_starter_pack import Farmbot
bot = Farmbot()
```

### Get your authentication token

Use the same login credentials associated with the web app account you are interacting with. The server is "https://my.farm.bot" by default.
```python
token = bot.get_token("email", "password")
```

To avoid storing your account credentials in plaintext, you can print your token:
```python
print(token)
```

and then delete the `bot.get_token("email", "password")` line and set your token directly instead:
```python
token = {'token': {'unencoded': {'aud': ...
bot.set_token(token)
```

where the part after `token = ` is the entire token pasted from the `print(token)` output. The start should look similar to the value above.

> [!CAUTION]
> Store your authorization token securely. It grants full access and control over your FarmBot and your FarmBot Web App account.

### Configure function output verbosity

Set the level of verbosity of function outputs to change the level of information shown when functions are called.
```python
bot.set_verbosity(2)
```

| Verbosity | Example using `e_stop()` |
| :--- | :--- |
| `0` The function will return with no output. | No output. |
| `1` A description of the action will be output with any additional results data. | `Emergency stopping device` |
| `2` The name of the function and the timestamp will be output. | `'e_stop()' called at: 2024-08-21 11:16:18.547813` |

### Test 1: Add a new plant to your garden

This test will help familiarize you with sending commands via the [API](https://developer.farm.bot/docs/rest-api).
```python
new_cabbage = {
    "name": "Cabbage",              # Point name
    "pointer_type": "Plant",        # Point type
    "x": 400,                       # x-coordinate
    "y": 300,                       # y-coordinate
    "z": 0,                         # z-coordinate
    "openfarm_slug": "cabbage",     # Plant type
    "plant_stage": "planned",       # Point status
}

bot.api_post("points", new_cabbage) # Add plant to endpoint
```

### Test 2: Turn your LED strip on and off

This test will help familiarize you with sending commands via the [Message Broker](https://developer.farm.bot/docs/message-broker).
```python
bot.on(7)           # Turn ON pin 7 (LED strip)
bot.wait(2000)      # Wait 2000 milliseconds
bot.off(7)          # Turn OFF pin 7 (LED strip)
```

## :compass: Functions

```
sidecar-starter-pack/
├── functions/
│   ├── __init_.py
│   ├── api.py
│   ├── basic_commands.py
│   ├── broker.py
│   ├── camera.py
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
├── main.py
└── README.md
```

### api.py

| class `ApiConnect()` | Description |
| :--- | :--- |
| `get_token()` | Get FarmBot authorization token. Server is "https://my.farm.bot" by default. |
| `set_token()` | Set FarmBot authorization token. |
| `check_token()` | Ensure the token persists throughout sidecar. |
| `request_handling()` | Handle errors associated with different endpoint errors. |
| `request()` | Make requests to API endpoints using different methods. |

### basic_commands.py

| class `BasicCommands()` | Description |
| :--- | :--- |
| `wait()` | Pauses FarmBot execution for a certain number of milliseconds. |
| `e_stop()` | Emergency locks (E-stops) the Farmduino microcontroller and resets peripheral pins to OFF. |
| `unlock()` | Unlocks a locked (E-stopped) device. |
| `reboot()` | Reboots FarmBot OS and reinitializes the device. |
| `shutdown()` | Shuts down FarmBot OS, turning the device off. Note: You will need to unplug and plug the FarmBot back in to turn it back on. |

### broker.py

| class `BrokerConnect()` | Description |
| :--- | :--- |
| `connect()` | Establish a persistent connection to send messages via the message broker. |
| `disconnect()` | Disconnect from the message broker. |
| `publish()` | Publish messages containing CeleryScript via the message broker. |
| `start_listen()` | Establish persistent subscription to message broker channels. |
| `stop_listen()` | End subscription to all message broker channels. |
| `listen()` | Listen to a message broker channel for the provided duration in seconds. |

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
> Not sure which endpoint to access? [Find the list here](https://developer.farm.bot/docs/api-docs).

| class `Information()` | Description |
| :--- | :--- |
| `api_get()` | GET information from the API. |
| `api_patch()` | PATCH information in the API. |
| `api_post()` | POST information to the API. |
| `api_delete()` | DELETE information in the API. |
| `safe_z()` | Returns the safe Z coordinate. |
| `garden_size()` | Returns size of garden bed. |
| `group()` | Returns all groups or a single group by id. |
| `curve()` | Returns all curves or a single curve by id. |
| `measure_soil_height()` | Use the camera to determine soil height at the current location. |
| `read_status()` | Returns the FarmBot status tree. |
| `read_sensor()` | Reads the given sensor. |

### jobs.py

| class `JobHandling()` | Description |
| :--- | :--- |
| `get_job()` | Retrieves the status or details of the specified job. |
| `set_job()` | Initiates or modifies job with given parameters. |
| `complete_job()` | Marks job as completed. |

### messages.py

| class `MessageHandling()` | Description |
| :--- | :--- |
| `log()` | Sends new log message via the API. Requires the web app page to be refreshed before appearing. |
| `message()` | Sends new log message via the message broker. |
| `debug()` | Sends debug message used for developer information or troubleshooting. These will not persist in the database. |
| `toast()` | Sends a message that pops up in the web app briefly. |

### movements.py

| class `MovementControls()` | Description |
| :--- | :--- |
| `move()` | Moves to the specified (x, y, z) coordinate. |
| `set_home()` | Sets the current position as the home position for a specific axis. |
| `find_home()` | Moves the device to the home position for a specified axis. |
| `find_axis_length()` | Finds the length of a specified axis. |
| `get_xyz()` | Returns the current (x, y, z) coordinates of the FarmBot. |
| `check_position()` | Verifies the current position of the FarmBot is within the specified tolerance range. |

### peripherals.py

| class `Peripherals()` | Description |
| :--- | :--- |
| `control_servo()` | Set servo angle between 0-100 degrees. |
| `control_peripheral()` | Set peripheral value (digital ON/OFF or analog value from 0-255). |
| `toggle_peripheral()` | Toggles the state of a specific peripheral between 'ON' (100%) and 'OFF' (0%). |
| `on()` | Turns specified pin number 'ON' (100%). |
| `off()` | Turns specified pin number 'OFF' (0%). |

### resources.py

| class `Resources()` | Description |
| :--- | :--- |
| `sequence()` | Executes a predefined sequence by name. |
| `get_seed_tray_cell()` | Returns the coordinates of the specified cell in a seed tray. |
| `detect_weeds()` | Scans the garden to detect weeds. |
| `lua()` | Executes custom Lua code snippets to perform complex tasks or automations. |
| `if_statement()` | Performs conditional check and executes actions based on the outcome. |
| `assertion()` | Evaluates an expression. |
<!--- | `sort_points()` | Sorts list of points (e.g., plants, weeds) based on specified criteria. | --->

### tools.py

| class `ToolControls()` | Description |
| :--- | :--- |
| `mount_tool()` | Mounts the given tool and pulls it out of its assigned slot. |
| `dismount_tool()` | Dismounts the currently mounted tool into its assigned slot. |
| `water()` | Moves to and waters a plant based on its age and assigned watering curve. |
| `dispense()` | Dispenses user-defined amount of liquid in milliliters. |
<!--- | `verify_tool()` | Verifies if tool is mounted to UTM via tool verification pin and MOUNTED TOOL field in FarmBot’s state tree. | --->

## :toolbox: Developer Info

### Formatting message broker messages

> [!NOTE]
> Messages sent via the message broker contain [CeleryScript nodes](https://developer.farm.bot/docs/nodes) which require special formatting.

```python
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

### Local development

If you are working on the sidecar-starter-pack itself,

(1) Clone the repository.
```bash
git clone https://github.com/FarmBot-Labs/sidecar-starter-pack
```

(2) Navigate to the project directory.
```bash
cd sidecar-starter-pack
```

(3) Create a virtual environment.
```bash
python -m venv py_venv
```

(4) Activate the virtual environment.
```bash
source py_venv/bin/activate
```

(5) Install the required libraries within the virtual environment:
```bash
python -m pip install requests paho-mqtt coverage
```

Ensure any changes pass all tests before submitting a pull request.

```bash
coverage run -m unittest discover
coverage html
```

You can review test coverage by opening `htmlcov/index.html` in a browser.

### Uploading package to PyPI (For FarmBot employees)

Follow [this tutorial](https://packaging.python.org/en/latest/tutorials/packaging-projects/).
```bash
python -m pip install --upgrade pip build twine
rm dist/*
python -m build
python -m twine upload dist/*
```
