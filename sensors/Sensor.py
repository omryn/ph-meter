__author__ = 'Omry_Nachman'


class Sensor:
    def __init__(self, name, check_func, pre_check=None, post_check=None):
        self.name = name
        self.checkProc = check_func
        self.initProc = pre_check
        self.cleanupProc = post_check

    def check(self):
        if self.initProc:
            self.initProc()
        result = self.check()
        if self.cleanupProc:
            self.cleanupProc()
        return result