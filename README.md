# sidecar-starter-pack
Authentication and communication utilities for FarmBot sidecars

## :book: Contents

* [Installation](#computer-installation-mac-os)
* [Getting Started](#seedling-getting-started)
    * [Get your authentication token](#get-your-authentication-token)
    * [Configure echo and verbosity](#configure-echo-and-verbosity)
* [Functions](#compass-functions)
* [Developer Info](#toolbox-developer-info)
    * [Formatting message broker messages](#formatting-message-broker-messages)
    * [Formatting API requests](#formatting-api-requests)

## :computer: Installation (Mac OS)

## :seedling: Getting Started

Import `main.py` and create an instance of the Farmbot class:
```
from main.py import Farmbot
bot = Farmbot()
```

### Get your authentication token

### Configure echo and verbosity

## :compass: Functions

```
sidecar-starter-pack/
├── functions/
│   ├── __init__.py
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
│   ├── __init__.py
│   └── tests_main.py
├── __init.py__
├── imports.py
├── main.py
└── README.md
```

> [!TIP]
> Functions marked with [API] communicate with the Farm Designer web app via the [REST API](https://developer.farm.bot/v15/docs/web-app/rest-api.html) and those marked with [BROKER] communicate with the FarmBot via the [message broker](https://developer.farm.bot/v15/docs/message-broker).

### authentication.py
class `Authentication()`

### basic_commands.py
class `BasicCommands()`

### broker.py
class `BrokerConnect()`

### camera.py
class `Camera()`

### information.py
class `Information()`

> [!CAUTION]
> Making requests other than `GET` to the API will permanently alter the data in your account. `DELETE` and `POST` requests may destroy data that cannot be recovered. Altering data through the API may cause account instability.

> [!NOTE]
> Not sure which endpoint to access? [Find the list here](https://developer.farm.bot/v15/docs/web-app/api-docs).

### jobs.py
class `JobHandling()`

### messages.py
class `MessageHandling()`

### movement.py
class `MovementControls()`

### peripherals.py
class `Peripherals()`

### resources.py
class `Resources()`

### tools.py
class `ToolControls()`

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

### Formatting API requests