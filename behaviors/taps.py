__author__ = 'Omry_Nachman'
from time import sleep


class Tap(object):
    def __init__(self, pi_face, output_pin, open_value=True):
        self.pi_face = pi_face
        self.output_pin = output_pin
        self.open_value = open_value
        self.state = None
        self.close()

    def switch(self, open_tap=True):
        self.state = open_tap
        if open_tap:
            self.pi_face.output_pins[self.output_pin].value = self.open_value
        else:
            self.pi_face.output_pins[self.output_pin].value = not self.open_value

    def open(self):
        self.switch(True)

    def close(self):
        self.switch(False)

    def toggle(self):
        self.switch(not self.state)

    def flick(self, duration, return_lambda=False, off_on_off=True):
        def execute():
            self.switch(not off_on_off)
            sleep(duration)
            self.switch(off_on_off)

        if return_lambda:
            return execute
        else:
            execute()


class DCTap(Tap):
    def __init__(self, pi_face, charge_discharge_pin=6, discharge_value=False, open_close_pin=7, open_value=False):
        self.pi_face = pi_face
        self.charge_discharge_pin = charge_discharge_pin
        self.discharge_value = discharge_value
        self.open_close_pin = open_close_pin
        self.open_value = open_value
        self.state = None
        self.close()

    def switch(self, open_tap=True):
        self.state = open_tap
        if open_tap:
            direction = self.open_value
        else:
            direction = not self.open_value

        self.pi_face.output_pins[self.charge_discharge_pin].value = not self.discharge_value
        self.pi_face.output_pins[self.charge_discharge_pin].value = direction
        sleep(0.1)
        self.pi_face.output_pins[self.charge_discharge_pin].value = self.discharge_value
        sleep(0.1)
        self.pi_face.output_pins[self.charge_discharge_pin].value = not self.discharge_value
