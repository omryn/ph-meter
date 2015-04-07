__author__ = 'Omry_Nachman'

import time


def noop():
    return None


class RetryPolicy(object):
    def __init__(self, wait_before_recheck=10, max_retries=10, recheck_when=True,
                 recheck_on_error=True, on_failed_all=noop):
        self.wait_before_recheck = wait_before_recheck
        self.recheck_when = recheck_when
        self.recheck_on_error = recheck_on_error
        self.max_retries = max_retries
        self.on_failed_all = on_failed_all

    def should_retry(self, condition_satisfied, measured, reties_count):
        if reties_count >= self.max_retries:
            self.on_failed_all()
            return False
        if isinstance(measured, Exception) and self.recheck_on_error:
            return self._deleyed_true()
        if condition_satisfied == self.recheck_when:
            return self._deleyed_true()
        return False

    def _deleyed_true(self):
        time.sleep(self.wait_before_recheck)
        return True

    @staticmethod
    def no_retry():
        return RetryPolicy(0, 0)

    @staticmethod
    def retry_on_error(delay=1, retries=60, on_final_error=noop):
        return RetryPolicy(delay, retries, None, on_failed_all=on_final_error)


class Behavior:
    def __init__(self, name, sensor, condition_func,
                 on_true=noop, on_false=noop, on_error=noop,
                 retry_policy=RetryPolicy.no_retry(), log=lambda x: None):
        self.name = name
        self.sensor = sensor
        self.condition_func = condition_func
        self.on_true = on_true
        self.on_false = on_false
        self.on_error = on_error
        self.retry_policy = retry_policy
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
            self.log("Measure failed: %s" % err)
            measure = err
            condition_satisfied = None
            self.on_error()

        samples.append(measure)

        if self.retry_policy.should_retry(condition_satisfied, measure, itteration_count):
            self.log("Retry %d" % itteration_count)
            return self.execute(itteration_count + 1, samples, start_time)
        else:
            return {
                'samples': samples,
                'status': condition_satisfied,
                'retries': itteration_count,
                'duration': time.time() - start_time
            }