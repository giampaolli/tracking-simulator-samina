import threading
import logging
import time
import json
from random import randint
import numpy as np
import paho.mqtt.client as mqtt
from geopy import Point
from geopy import distance


class Simulator:
    MIN_SLEEP_TIME = 599      # 9 min 59 seconds
    MAX_SLEEP_TIME = 600     # 10 min
    MIN_DISPLACEMENT = 0    # 0 Km
    MAX_DISPLACEMENT = 0.1 # 0.1 Km
    MIN_BEARING = 0    # 0 degree
    MAX_BEARING = 360  # 360 degrees
    MAX_DISPLACEMENT_FROM_ORIGIN = 100  # 25 Km
    MEAN_TEMPERATURE = 35
    MEAN_HUMIDITY = 60
    MEAN_PRECISION = 3000
    MEAN_BATTERY= 3
    MEAN_TYPE= 0
    MEAN_SEVERITY= 3

    def __init__(self, host, port, tenant, device, latitude, longitude, movement):
        self.__logger = logging.getLogger('trackingsim.sim')
        self.__origin = Point(latitude, longitude)
        self.__current_position = Point(latitude, longitude)
        self.__mqttc = mqtt.Client(str(threading.current_thread().ident))
        self.__mqttc.connect(host=host, port=port)
        self.__mqttc.loop_start()
        self.__topic = "/{0}/{1}/attrs".format(tenant, device)
        self.__sleep = np.random.uniform(self.__class__.MIN_SLEEP_TIME, self.__class__.MAX_SLEEP_TIME)
        self.__logger.info("Starting simulation for device {0} with sleep time {1}".format(device, self.__sleep))

        if movement == 'straight-line':
            self.__next_movement = self.__get_next_position_for_straight_line
        elif movement == 'static':
            self.__next_movement = self.__get_static_position
        else:
            self.__next_movement = self.__get_next_random_position

        # bearing displacement used in the last movement. Start with random values
        self.__displacement = \
            np.random.uniform(self.__class__.MIN_DISPLACEMENT, self.__class__.MAX_DISPLACEMENT)
        self.__bearing = \
            np.random.uniform(self.__class__.MIN_BEARING, self.__class__.MAX_BEARING)

    def run(self):
        while True:
            data = dict()

            # gps
            data['gps'] = "{0}, {1}".format(str(self.__current_position.latitude),
                                            str(self.__current_position.longitude))
            # sinr
            # data['sinr'] = self.__get_next_sinr()

            # batteryVoltage
            # data['batteryVoltage'] = np.random.normal(self.MEAN_BATTERY)
            data['batteryVoltage'] = 3

            # temperatureCelsius
            data['temperatureCelsius'] = np.random.normal(self.MEAN_TEMPERATURE)

            # relativeHumidity
            data['relativeHumidity'] = np.random.normal(self.MEAN_HUMIDITY)

            # precision
            data['precision'] = np.random.normal(self.MEAN_PRECISION)

            # type
            data['type'] = 0

            # severity
            data['severity'] = randint(self.MEAN_TYPE, self.MEAN_SEVERITY)

            # publish
            self.__logger.info("Publishing: {0}".format(json.dumps(data)))
            self.__mqttc.publish(self.__topic, json.dumps(data))

            # sleep
            time.sleep(self.__sleep)

            # next position
            (self.__current_position, self.__displacement, self.__bearing) = \
                self.__next_movement()

    def __get_next_random_position(self):
        # displacement
        displacement = np.random.uniform(self.__class__.MIN_DISPLACEMENT, self.__class__.MAX_DISPLACEMENT)

        # direction
        bearing = np.random.uniform(self.__class__.MIN_BEARING, self.__class__.MAX_BEARING)

        # next point
        next_position = distance.vincenty(kilometers=displacement).destination(self.__current_position, bearing)
        while (distance.vincenty(self.__origin, next_position).kilometers
                   > self.__class__.MAX_DISPLACEMENT_FROM_ORIGIN):
            # displacement
            displacement = np.random.uniform(self.__class__.MIN_DISPLACEMENT, self.__class__.MAX_DISPLACEMENT)

            # direction
            bearing = np.random.uniform(self.__class__.MIN_BEARING, self.__class__.MAX_BEARING)

            # next point
            next_position = distance.vincenty(kilometers=displacement).destination(self.__current_position, bearing)

        return next_position, displacement, bearing

    def __get_next_position_for_straight_line(self):
        # displacement
        displacement = np.random.uniform(self.__class__.MIN_DISPLACEMENT, self.__class__.MAX_DISPLACEMENT)

        # direction
        bearing = self.__bearing

        # next point
        next_position = distance.vincenty(kilometers=displacement).destination(self.__current_position, bearing)
        if (distance.vincenty(self.__origin, next_position).kilometers
                   > self.__class__.MAX_DISPLACEMENT_FROM_ORIGIN):

            # direction
            bearing = (self.__bearing + 180) % 360

            # next point
            next_position = distance.vincenty(kilometers=displacement).destination(self.__current_position, bearing)

        return next_position, displacement, bearing
    
    def __get_static_position(self):
        return self.__current_position
 

    def __get_next_sinr(self):
        displacement_from_origin = distance.vincenty(self.__origin, self.__current_position).kilometers
        relative_displacement = displacement_from_origin / self.MAX_DISPLACEMENT_FROM_ORIGIN

        if relative_displacement < 0.15:
            sinr = np.random.uniform(20, 30)

        elif relative_displacement < 0.30:
            sinr = np.random.uniform(15, 20)

        elif relative_displacement < 0.45:
            sinr = np.random.uniform(10, 15)

        elif relative_displacement < 0.60:
            sinr = np.random.uniform(5, 10)

        elif relative_displacement < 0.75:
            sinr = np.random.uniform(2, 5)

        else:
            sinr = np.random.uniform(-1, 2)

        return sinr
