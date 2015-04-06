#!/usr/bin/env python
__author__ = 'Omry_Nachman'

from beheaviors import SchedulerWithConfig
import signal
import sys
from config import home


def log(x):
    print x

scheduler = SchedulerWithConfig(log=log)


def signal_handler(signal, frame):
    global scheduler
    scheduler.kill()
    scheduler.join(1)
    sys.exit(1)
signal.signal(signal.SIGINT, signal_handler)

print "Stating scheduler"
scheduler.start()
scheduler.add_schedule(home.schedule)

while True:
    signal.pause()
