__author__ = 'Omry_Nachman'


def noop():
    pass


class ConditionHandler:
    def __init__(self, sensor, condition_func, on_true=noop, on_false=noop):
        self.sensor = sensor
        self.condition_func = condition_func
        self.on_true = on_true
        self.on_false = on_false

    def execute(self):
        result = self.sensor.check()
        if self.condition_func(result):
            self.on_true()
        else:
            self.on_false()