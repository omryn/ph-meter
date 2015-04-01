__author__ = 'Omry_Nachman'
import Sensor

class LinearCalibratedSensor(Sensor):
    def __init__(self, name, check_func, pre_check=None, post_check=None):
        super(LinearCalibratedSensor, self).__init__(name, check_func, pre_check, post_check)
        self.calibration_points = {}

    def add_calibration_point(self, nominal_value, measured_value=None):
        if measured_value == None:
            measured_value = super(LinearCalibratedSensor, self).check()
        self.calibration_points[nominal_value] = measured_value

    def check(self):
        measured_value = super(LinearCalibratedSensor, self).check()
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