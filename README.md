# sidecar-starter-pack
Authentication and communication utilities for FarmBot sidecars

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

## 🏁 Getting Started
To generate your authorization token and get started:

(1) Import `farmbot_utilities` and create an instance.
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

(4.1) To interact with your Farmbot via the message broker, first establish a connection:
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

## 🔬 Developer Info

sidecar-starter-pack/
│
├── farmbot_utilities.py
│   └── class Farmbot
│
├── farmbot_API.py
│   └── class FarmbotAPI
│
└── farmbot_BROKER.py
    └── class FarmbotBroker

`farmbot_API`
Background: https://developer.farm.bot/v15/docs/web-app/rest-api
Formatting: functions in `farmbot_utilities` which interact with the API require an endpoint, which is truncated onto the HTTP request.

List of endpoints: https://developer.farm.bot/v15/docs/web-app/api-docs

`farmbot_BROKER`
Background: https://developer.farm.bot/v15/docs/message-broker
Formatting: functions in `farmbot_utilities` which interact with the message broker send a message containing CelerScript. The messages require the pre-formatted `RPC_request` included in `farmbot_utilities` as the first line of the message.