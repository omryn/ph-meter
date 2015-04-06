__author__ = 'Omry_Nachman'

from config import home
from time import sleep


def sample(sensor=home.moisture):
    while True:
        print sensor.measure()
        sleep(0.2)