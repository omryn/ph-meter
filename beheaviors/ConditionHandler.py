__author__ = 'Omry_Nachman'

import time


def noop():
    return None


class ConditionHandler:
    def __init__(self, name, sensor, condition_func, on_true=noop, on_false=noop,
                 recheck_interval=120, max_checks=10, recheck_on=True):
        self.name = name
        self.sensor = sensor
        self.condition_func = condition_func
        self.on_true = on_true
        self.on_false = on_false
        self.recheck_interval = recheck_interval
        self.max_checks = max_checks
        self.recheck_on = recheck_on

    def execute(self, itteration_count=0, samples=[], start_time=time.time()):
        try:
            measure = self.sensor.measure()
            condition_satisfied = self.condition_func(measure)
            if condition_satisfied:
                self.on_true()
            else:
                self.on_false()
        except Exception as err:
            measure = err

        samples.append(measure)

        if isinstance(measure, Exception) or \
                (condition_satisfied == self.recheck_on and itteration_count < self.max_checks):
            time.sleep(self.recheck_interval)
            return self.execute(itteration_count + 1, samples, start_time)
        else:
            return {
                'samples': samples,
                'status': condition_satisfied,
                'duration': time.time() - start_time
            }