import logging
import threading
from optparse import OptionParser
from trackingsim.sim import Simulator
from trackingsim.devices import (create_devices, remove_devices)

# set logger
logger = logging.getLogger('trackingsim')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - Thread %(thread)d - %(levelname)s - %(message)s')
channel = logging.StreamHandler()
channel.setFormatter(formatter)
logger.addHandler(channel)


# thread
def worker(host, port, service, device, latitude, longitude, movement):
    s = Simulator(host, port, service, device, latitude, longitude, movement)
    s.run()


if __name__ == '__main__':
    # parse arguments
    parser = OptionParser()

    # MQTT broker - IP
    parser.add_option("-H", "--host", dest="host", default="127.0.0.1",
                      help="Host to connect. Defaults to localhost.")

    # MQTT broker - Port
    parser.add_option("-P", "--port", dest="port", type="int", default=1883,
                      help="Port to connect to. Defaults to 1883.")

    # API Gateway - IP
    parser.add_option("-G", "--api-gateway", dest="gw", default="127.0.0.1",
                      help="API Gateway to connect to. Defaults to localhost.")

    # dojot - Tenant ID
    parser.add_option("-t", "--tenant", dest="tenant", default="admin",
                      help="Tenant identifier in dojot. Defaults to admin.")

    # dojot - User ID
    parser.add_option("-u", "--user", dest="user", default="admin",
                      help="User identifier in dojot. Defaults to admin.")

    # dojot - User password
    parser.add_option("-p", "--password", dest="password", default="admin",
                      help="User password in dojot. Defaults to admin.")

    # dojot - https or http
    parser.add_option("-s", action="store_true", dest="secure", default=False,
                      help="Enables https communication with dojot.")

    # dojot - prefix
    parser.add_option("-l", "--prefix", dest="prefix", default="trackingsim",
                      help="Label prefix for templates and devices. Defaults to trackingsim.")

    # dojot - Remove templates and devices whose names start with trackingsim prefix
    parser.add_option("-c", "--clear", action="store_true", dest="clear",
                      help="Remove all templates and devices whose names start with "
                           "trackingsim prefix. Default disabled.")

    # dojot - Number of devices to be created
    parser.add_option("-n", "--number_of_devices", dest="number_of_devices", type="int", default=0,
                      help="Number of devices to be created [1..128]. Defaults to 0.")

    # dojot - Device ID list
    parser.add_option("-d", "--device", dest="devices", default=[], action="append",
                      help="Device identifier in dojot. Multiple devices can be simulated "
                           "simultaneously repeating this option.")

    # Simulation - Starting latitude
    parser.add_option("-x", "--latitude", dest="latitude", default="-23.559613",
                      help="Starting latitude for the simulation. Defaults to -23.559613.")

    # Simulation - Starting longitude
    parser.add_option("-y", "--longitude", dest="longitude", default="-46.663665",
                      help="Starting longitude for the simulation. Defaults to -46.663665.")

    # Simulation - Type of movement (random or straight-line)
    parser.add_option("-m", "--movement", dest="movement", default="straight-line",
                      help="Type of movement (straight-line or random) for the simulation. "
                           "Defaults to straight-line.")

    (options, args) = parser.parse_args()
    logger.info("Options: {}".format(options))

    # validate parameters
    if options.movement != 'straight-line' and options.movement != 'random' and options.movement != 'static':
        logger.error("The type of movement {} is invalid. It must be straight-line, random or static.",
                     options.movement)
        exit(-1)

    if options.number_of_devices < 0 or options.number_of_devices > 500:
        logger.error("The number of devices must be in [0..500].")
        exit(-2)

    # remove devices and templates from earlier runs
    if options.clear:
        remove_devices(options.secure, options.gw, options.user,
                       options.password, options.prefix)

    # create templates and devices
    devices = []
    if options.number_of_devices > 0:
        devices = create_devices(options.secure,
                                 options.gw,
                                 options.user,
                                 options.password,
                                 options.number_of_devices,
                                 options.prefix)

    # run one thread for each device
    devices = devices + options.devices
    if devices:
        for device_id in devices:
            logger.info("Starting thread for device {}".format(device_id))
            t = threading.Thread(target=worker, args=(options.host, options.port, options.tenant,
                                                      device_id, options.latitude, options.longitude,
                                                      options.movement))
            t.start()
    else:
        logger.info("Finishing! There is not device to simulate.")
