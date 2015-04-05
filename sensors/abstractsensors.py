__author__ = 'Omry_Nachman'
from numpy import median, std, mean
from time import time

class Sensor:
    def __init__(self, name, measure_func, pre_measure=None, post_measure=None, samples_count=10, max_std=None):
        self.name = name
        self.measureProc = measure_func
        self.initProc = pre_measure
        self.cleanupProc = post_measure
        self.samples_count = samples_count
        self.max_std = max_std

    def measure(self):
        if self.initProc:
            self.initProc()

        samples = [self.measureProc() for count in range(self.samples_count)]
        if self.max_std and std(samples) > self.max_std:
            raise MeasureError(self.name, samples, self.max_std)

        if self.cleanupProc:
            self.cleanupProc()
        return median(samples)


class LinearCalibratedSensor(Sensor):
    def __init__(self, name, measure_func, pre_measure=None, post_measure=None, samples_count=10, max_std=None):
        super(LinearCalibratedSensor, self).__init__(name, measure_func, pre_measure, post_measure, samples_count, max_std)
        self.calibration_points = {}

    def add_calibration_point(self, nominal_value, measured_value=None):
        if not measured_value:
            measured_value = self.measure_raw()
        self.calibration_points[nominal_value] = measured_value

    def measure_raw(self):
        return super(LinearCalibratedSensor, self).measure()

    def measure(self):
        measured_value = self.measure_raw()
        return self.get_nominal_value(measured_value)

    def get_nominal_value(self, measured_value):
        assert len(self.calibration_points) > 0, "No calibration points added, use add_calibration_point"

        if len(self.calibration_points) == 1:
            calibration = self.calibration_points.items()[0]
            return calibration[0] + measured_value - calibration[1]

        cal_range = self._get_closest_range(measured_value)
        diff_nominal = cal_range[1][0] - cal_range[0][0]
        diff_measured = cal_range[1][1] - cal_range[0][1]
        m = diff_nominal / diff_measured
        f = lambda x: cal_range[0][1] + m*(x - cal_range[0][0])
        return f(measured_value)

    def _get_closest_range(self, measured_value):
        calibration = self.calibrationPoints.items().sort(lambda a, b: b[1]-a[1])
        under = filter(calibration, lambda item: measured_value <= item[1])
        over = filter(calibration, lambda item: measured_value > item[1])

        if len(under) > 0 & & len(over) > 0:
            return [under[-1], over[0]]
        elif len(under) == 0:
            return over[0:2]
        else:
            return under[-2:]

class MeasureError(Exception):
    def __init__(self, name, samples, max_std):
        self.name = name
        self.samples = samples
        self.max_std = max_std
        self.std = std(samples)
        self.median = median(samples)
        self.mean = mean(samples)
        self.time_stamp = time()