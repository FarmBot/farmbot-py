# sidecar-starter-pack
Authentication and communication utilities for FarmBot sidecars

## 📖 Contents

* [Installation](#-installation-mac-os)
* [Getting Started](#-getting-started)
* [Functions](#-functions)
    * [Setup](#setup)
    * [Information](#information)
    * [Messaging](#messaging)
    * [Basic Commands](#basic-commands)
    * [Movement](#movement)
    * [Peripherals](#peripherals)
    * [Broker Commands](#broker-commands)
* [Developer Info](#-developer-info)
    * [api_connect.py](#api_connectpy)
    * [broker_connect.py](#broker_connectpy)

## 💻 Installation (Mac OS)
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

## 🌱 Getting Started
To generate your authorization token and get started:

(1) Import `main.py` and create an instance.
```
from farmbot_utilities import Farmbot
bot = Farmbot()
```

(2) Generate your authorization token.
    The server is https://my.farm.bot by default.
```
bot.get_token('email', 'password', 'server')
```

(3.1) To interact with your Farmbot via the API, try getting your device info:
```
bot.get_info('device')
```

(3.2) Try editing your device name:
```
bot.edit_info('device', 'name', 'Carrot Commander')
```
> [!NOTE]
> To interact with your Farmbot via the message broker, you must first establish a connection. Publishing single messages without establishing a connection may trigger your device rate limit.

(4.1) Connect to the message broker:
```
bot.connect_broker()
```

(4.2) Try sending a new log message:
```
bot.send_message('Hello from the message broker!', 'success')
```

(4.3) Try sending a movement command:
```
bot.move(30,40,10)
```

(4.5) After sending messages, don't forget to disconnect from the message broker:
```
bot.disconnect_broker()
```

## 🧭 Functions

### Setup

`get_token()` generates user authentication token; call before any other function
`connect_broker()` establishes persistent connect to message broker
`disconnect_broker()` disconnects from the message broker
`listen_broker()` displays messages sent to/from message broker

### Information

`get_info()` returns information about a specific endpoint
`set_info()` edits information belonging to preexisting endpoint
env()
group()
curve()
read_status()
read_sensor()
safe_z()
garden_size()

### Messaging

`log()` sends a new log message via the API
`message()` sends a new log message via the message broker
`debug()` sends a log message of type 'debug' via the message broker
`toast()` sends a log message of type 'toast' via the message broker

### Basic Commands

wait()
e_stop()
unlock()
reboot()
shutdown()

### Movement

move()
set_home()
find_home()
axis_length()

### Peripherals

control_peripheral()
toggle_peripheral()
on()
off()

### Broker Commands

calibrate_camera()
control_servo()
take_photo()
soil_height()
detect_weeds()

## 🧰 Developer Info

### api_connect.py
Background: https://developer.farm.bot/v15/docs/web-app/rest-api

Formatting: functions in `api_functions.py` and `main.py` which interact with the API require an endpoint, which is truncated onto the HTTP request.

List of endpoints: https://developer.farm.bot/v15/docs/web-app/api-docs

> [!CAUTION]
> Making requests other than GET to the API will permanently alter the data in your account. DELETE and POST requests may destroy data that cannot be recovered. Altering data through the API may cause account instability.

### broker_connect.py
Background: https://developer.farm.bot/v15/docs/message-broker

Formatting: functions in `broker_functions.py` and `main.py` which interact with the message broker send a message containing CeleryScript. The messages require the pre-formatted `RPC_request` included in `broker_functions.py` as the first line of the message.