__author__ = 'Omry_Nachman'

import time


def noop():
    return None


class ConditionHandler:
    def __init__(self, name, sensor, condition_func, on_true=noop, on_false=noop,
                 recheck_interval=None, max_checks=10, recheck_on=True, log=lambda: None):
        self.name = name
        self.sensor = sensor
        self.condition_func = condition_func
        self.on_true = on_true
        self.on_false = on_false
        self.recheck_interval = recheck_interval
        self.max_checks = max_checks
        self.recheck_on = recheck_on
        self.log = lambda x: log("%s<ConditionHandler>: %s" % (name, x))

    def execute(self, itteration_count=0, samples=None, start_time=None):
        if samples is None: samples = []
        if start_time is None: start_time = time.time()
        
        try:
            measure = self.sensor.measure()
            condition_satisfied = self.condition_func(measure)
            self.log("Measured %.2f, condition_satisfied=%r" % (measure, condition_satisfied))
            if condition_satisfied:
                self.on_true()
            else:
                self.on_false()
        except Exception as err:
            measure = err

        samples.append(measure)

        if self.recheck_interval is not None and (
                    isinstance(measure, Exception) or
                    (condition_satisfied == self.recheck_on and itteration_count < self.max_checks)):
            time.sleep(self.recheck_interval)
            return self.execute(itteration_count + 1, samples, start_time)
        else:
            return {
                'samples': samples,
                'status': condition_satisfied,
                'duration': time.time() - start_time
            }