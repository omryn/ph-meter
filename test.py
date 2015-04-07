__author__ = 'Omry_Nachman'

from config import home
from time import sleep
from behaviors import *
from sensors import *


def sample(sensor=home.moisture):
    while True:
        print sensor.measure()
        sleep(0.2)



