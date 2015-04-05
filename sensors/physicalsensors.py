__author__ = 'Omry_Nachman'

from Adafruit_ADS1x15 import ADS1x15
from pifacedigitalio import PiFaceDigital
from time import sleep
import abstractsensors


class SensorWithPower(abstractsensors.Sensor):
    def __init__(self, name, power_pin=2, ads_channel=1, pga=4096,
                 pi_face=PiFaceDigital(), ads=ADS1x15(ic=0, address=0x49),
                 max_std=None, min_value=0.6, max_value=4.0):

        super(SensorWithPower, self).__init__(name, self.get_measure,
                                              self.power_on, self.power_off,
                                              max_std=max_std, min_value=0.6, max_value=4.0)
        self.power_pin = power_pin
        self.ads_channel = ads_channel
        self.pga = pga
        self.ads = ads
        self.pi_face = pi_face

    def power_on(self):
        self.pi_face.output_pins[self.power_pin].turn_on()
        # Allow a small latency
        sleep(0.001)

    def power_off(self):
        self.pi_face.output_pins[self.power_pin].turn_off()

    def get_measure(self):
        """
        :return: a single sample (in Volts)
        """
        return self.ads.readADCSingleEnded(channel=self.ads_channel, sps=3300, pga=self.pga) / 1000


class PhSensor(abstractsensors.LinearCalibratedSensor):
    def __init__(self, name,  p_channel=2, n_channel=3, pga=512,
                 ads=ADS1x15(ic=0, address=0x49), max_std=None):
        super(PhSensor, self).__init__()
        super(PhSensor, self).__init__(name, self.get_measure,
                                       samples_count=20, max_std=max_std)
        self.p_channel = p_channel
        self.n_channel = n_channel
        self.pga = pga
        self.ads = ads

    def get_measure(self):
        return self.ads.readADCDifferential(self.p_channel, self.n_channel, self.pga, 3300)