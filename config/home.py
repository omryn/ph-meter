__author__ = 'Omry_Nachman'
from sensors import SensorWithPower, PhSensor, ADS1x15
from beheaviors import ConditionHandler
from pifacedigitalio import PiFaceDigital

### Hardware
piface = PiFaceDigital()
ads = ADS1x15(ic=0, address=0x49)

### Sensors
ph = PhSensor('ph', ads=ads)
moisture = SensorWithPower('moisture', ads=ads, pi_face=piface)
water_level = SensorWithPower('water level', power_pin=3, ads_channel=0, ads=ads, pi_face=piface, min_value=1)

### Behaviors
water_plants = ConditionHandler("water_plants", moisture,
                                lambda v: v < 3.7,
                                flick(piface.relays[0], 60), piface.relays[0].turn_off, piface.relays[0].turn_off,
                                RetryPolicy.retry_on_error(10, 20),
                                log=log)

balance_water_level = ConditionHandler("water_leveler", water_level,
                                 lambda v: v < 2.1,
                                 piface.relays[1].turn_on, piface.relays[1].turn_off, piface.relays[1].turn_off,
                                 RetryPolicy(1, 120, on_failed_all=piface.relays[1].turn_off),
                                 log=log)

### Schedule
schedule = [
    ('*/5 * * * *', water_plants),
    (10, balance_water_level)
]