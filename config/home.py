__author__ = 'Omry_Nachman'
from sensors import SensorWithPower, PhSensor, ADS1x15
from behaviors import *
from pifacedigitalio import PiFaceDigital

### Hardware
piface = PiFaceDigital()
ads = ADS1x15(ic=0, address=0x49)

### Sensors
ph = PhSensor('ph', ads=ads)
moisture = SensorWithPower('moisture', ads=ads, pi_face=piface)
water_level = SensorWithPower('water level', power_pin=3, ads_channel=0, ads=ads, pi_face=piface)

### Taps
plants_tap = Tap(piface, 0)
water_level_tap = Tap(piface, 1)
ph_up_tap = DCTap(piface)

### Behaviors
water_plants = Behavior("water_plants", moisture,
                        lambda v: v < 3.7,
                        plants_tap.flick(60, True), plants_tap.close, plants_tap.close,
                        RetryPolicy.retry_on_error(10, 20))

balance_water_level = Behavior("water_leveler", water_level,
                               lambda v: v < 2.2,
                               water_level_tap.open, water_level_tap.close, water_level_tap.close,
                               RetryPolicy(2, 120, on_failed_all=water_level_tap.close))

adjust_ph = Behavior("adjust_ph", ph,
                     lambda ph: ph < 8,
                     ph_up_tap.flick(10, True), ph_up_tap.close, ph_up_tap.close,
                     RetryPolicy(30, 20, on_failed_all=water_level_tap.close))

### Schedule
schedule = [
    ('*/15 * * * *', water_plants),
    (10, balance_water_level)
]