# tracking-simulator
It simulates a device moving from a starting point with sinr decreasing as
it distances itself from the origin. It also simulates temperature and rpm
from the engine.

The simulator sends data to dojot through MQTT with the following JSON payload:

```json
{"sinr": <value>,
 "gps": "<latitude-value>, <longitude-value>",
 "temperature": <value>,
 "rpm": <value>}
```

# Installation
To install the package requirements run:

```
$ pip3 install -r requirements.txt
```

# Usage
```
$ python3 -m trackingsim.main -h
Usage: main.py [options]

Options:
  -h, --help            show this help message and exit
  -H HOST, --host=HOST  Host to connect. Defaults to localhost.
  -P PORT, --port=PORT  Port to connect to. Defaults to 1883.
  -G GW, --api-gateway=GW
                        API Gateway to connect to. Defaults to localhost.
  -t TENANT, --tenant=TENANT
                        Tenant identifier in dojot. Defaults to admin
  -u USER, --user=USER  User identifier in dojot. Defaults to admin.
  -p PASSWORD, --password=PASSWORD
                        User password in dojot. Defaults to admin.
  -s                    Enables https communication with dojot.

  -l PREFIX, --prefix=PREFIX
                        Label prefix for templates and devices. Defaults to
                        trackingsim.
  -c, --clear           Remove all templates and devices whose names start
                        with trackingsim prefix. Default disabled.
  -n NUMBER_OF_DEVICES, --number_of_devices=NUMBER_OF_DEVICES
                        Number of devices to be created. Defaults to 0.
  -d DEVICES, --device=DEVICES
                        Device identifier in dojot. Multiple devices can be
                        simulated simultaneously repeating this option.
  -x LATITUDE, --latitude=LATITUDE
                        Starting latitude for the simulation. Defaults to
                        -22.815970.
  -y LONGITUDE, --longitude=LONGITUDE
                        Starting longitude for the simulation. Defaults to
                        -47.045121.
  -m MOVEMENT, --movement=MOVEMENT
                        Type of movement (straight-line or random) for the
                        simulation. Defaults to straight-line.
```