#!/usr/bin/python
__author__ = 'Omry_Nachman'

from beheaviors import Scheduler, ConditionHandler
from sensors import SensorWithPower, PhSensor, ADS1x15
from pifacedigitalio import PiFaceDigital
import signal
from time import sleep

def signal_handler(signal, frame):
    global scheduler
    scheduler.kill()
    scheduler.join(1)
signal.signal(signal.SIGINT, signal_handler)


scheduler = Scheduler(log=lambda x: print(x))
piface = PiFaceDigital()
ads = ADS1x15(ic=0, address=0x49)

ph = PhSensor('ph', ads=ads)
moisture = SensorWithPower('moisture', ads=ads, pi_face=piface)
water_level = SensorWithPower('water level', power_pin=3, ads_channel=0, ads=ads, pi_face=piface)


def flick(switchable, duration):
    def execute():
        switchable.turn_on()
        sleep(duration)
        switchable.turn_off()
    return execute

water_plants = ConditionHandler(moisture, lambda mv: mv < 3700, flick(piface.relays[0], 5), piface.relays[0].turn_off, 10)

scheduler.interval(water_plants, 30)

scheduler.start()
scheduler.join()
print "Good bye, hope you had a good time"
