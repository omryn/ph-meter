__author__ = 'Omry_Nachman'
from numpy import median, std, mean
from time import time


class Sensor(object):
    def __init__(self, name, measure_func, pre_measure=None, post_measure=None,
                 samples_count=10, max_std=None, min_value=None, max_value=None):
        self.name = name
        self.measureProc = measure_func
        self.initProc = pre_measure
        self.cleanupProc = post_measure
        self.samples_count = samples_count
        self.max_std = max_std
        self.min_value = min_value
        self.max_value = max_value

    def measure(self):
        if self.initProc:
            self.initProc()

        samples = [self.measureProc() for count in range(self.samples_count)]
        measured = median(samples)
        if self.max_std != None and std(samples) > self.max_std:
            raise StdTooHigh(self.name, samples, self.max_std)
        if self.min_value != None and measured < self.min_value:
            raise InvalidMeasuredValue(self.name, measured, self.min_value, self.max_value)
        if self.max_value != None and measured > self.max_value:
            raise InvalidMeasuredValue(self.name, measured, self.min_value, self.max_value)

        if self.cleanupProc:
            self.cleanupProc()
        return measured


class LinearCalibratedSensor(Sensor):
    def __init__(self, name, measure_func, pre_measure=None, post_measure=None,
                 samples_count=10, max_std=None, min_value=None, max_value=None):
        super(LinearCalibratedSensor, self).__init__(name, measure_func, pre_measure, post_measure, samples_count,
                                                     max_std, min_value, max_value)
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
        f = lambda x: cal_range[0][1] + m * (x - cal_range[0][0])
        return f(measured_value)

    def _get_closest_range(self, measured_value):
        calibration = self.calibrationPoints.items().sort(lambda a, b: b[1] - a[1])
        under = filter(calibration, lambda item: measured_value <= item[1])
        over = filter(calibration, lambda item: measured_value > item[1])

        if len(under) > 0 and len(over) > 0:
            return [under[-1], over[0]]
        elif len(under) == 0:
            return over[0:2]
        else:
            return under[-2:]


class MeasureError(Exception):
    def __init__(self, name):
        self.name = name
        self.time_stamp = time()

    def __str__(self):
        return "%s<Sensor> experience a sampling error" % self.name


class InvalidMeasuredValue(MeasureError):
    def __init__(self, name, value, min, max):
        super(InvalidMeasuredValue, self).__init__(name)
        self.value = value
        self.min = min
        self.max = max

    def __str__(self):
        return "%s: Sample not in expected range (value: %.2f, min: %0.2f, max: %0,2f)" % \
               (super(InvalidMeasuredValue, self).__str__(), self.value, self.min, self.max)


class StdTooHigh(MeasureError):
    def __init__(self, name, samples, max_std):
        super(InvalidMeasuredValue, self).__init__(name)
        self.samples = samples
        self.max_std = max_std
        self.std = std(samples)
        self.median = median(samples)
        self.mean = mean(samples)

    def __str__(self):
        return "%s: Samples STD too high (std: %.2f, max_std: %0,2f)\nSamples: %s" % \
               (super(InvalidMeasuredValue, self).__str__(), self.std, self.max_std, str(self.samples))