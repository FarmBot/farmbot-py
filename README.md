# sidecar-starter-pack
Authentication and communication utilities for FarmBot sidecars

## Installation (Mac OS)
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

## Getting Started
To generate your authorization token and get started:

(1) Import `farmbot-utilities` and create an instance.
```
from farmbot-utilities import Farmbot
bot = Farmbot()
```

(2) Generate your authorization token.
    The server is https://my.farm.bot by default.
```
bot.get_token('email', 'password', 'server')
```

(3.1) Try getting your device info:
```
print(bot.get_info('device'))
```

(3.2) Try sending a new log message:
```
bot.new_log_BROKER('Hello world!', 'success')
```