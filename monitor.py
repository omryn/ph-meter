#!/usr/bin/env python
__author__ = 'Omry_Nachman'

from beheaviors import Scheduler, ConditionHandler, RetryPolicy
from sensors import SensorWithPower, PhSensor, ADS1x15
from pifacedigitalio import PiFaceDigital
import signal
from time import sleep

print "Starting monitor"


def log(x):
    print x


scheduler = Scheduler(log=log)


def signal_handler(signal, frame):
    global scheduler
    print "Killing scheduler"
    scheduler.kill()
    scheduler.join(1)


signal.signal(signal.SIGINT, signal_handler)

piface = PiFaceDigital()
ads = ADS1x15(ic=0, address=0x49)

ph = PhSensor('ph', ads=ads)
moisture = SensorWithPower('moisture', ads=ads, pi_face=piface)
water_level = SensorWithPower('water level', power_pin=3, ads_channel=0, ads=ads, pi_face=piface, min_value=1)


def flick(switchable, duration):
    def execute():
        switchable.turn_on()
        sleep(duration)
        switchable.turn_off()

    return execute


water_plants = ConditionHandler("water_plants", moisture,
                                lambda v: v < 3.7,
                                flick(piface.relays[0], 60), piface.relays[0].turn_off, piface.relays[0].turn_off,
                                RetryPolicy.retry_on_error(10, 20),
                                log=log)

water_leveler = ConditionHandler("water_leveler", water_level,
                                 lambda v: v < 2.1,
                                 piface.relays[1].turn_on, piface.relays[1].turn_off, piface.relays[1].turn_off,
                                 RetryPolicy(1, 120, on_failed_all=piface.relays[1].turn_off),
                                 log=log)

print "Stating scheduler"
scheduler.start()
print "Adding water_plants"
scheduler.cron(water_plants, "* * * * *")
scheduler.interval(water_leveler, 30)
scheduler.join()
print "Good bye, hope you had a good time"
