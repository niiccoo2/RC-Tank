import board #type:ignore
import adafruit_qmc5883p #type:ignore
import math
from core import states
from time import sleep
from core.config import get_logger

compass = get_logger("compass")

class Compass:
    def __init__(self):
        self.i2c = board.I2C()
        self.sensor = adafruit_qmc5883p.QMC5883P(self.i2c)
        self.OFFSET_X = -0.198
        self.OFFSET_Y = 0.013
        self.SCALE_X = 0.84
        self.SCALE_Y = 0.73
        compass.debug("Compass initialized")
    
    def read_compass(self):
        raw_x, raw_y, raw_z = self.sensor.magnetic
    
        # Apply calibration
        cal_x = (raw_x - self.OFFSET_X) * self.SCALE_X
        cal_y = (raw_y - self.OFFSET_Y) * self.SCALE_Y
        
        # Calculate angle in radians, then convert to degrees
        heading = math.atan2(cal_x, cal_y) * (180 / math.pi)
        
        heading = heading-13.75-93  # that is the magnetic difference for boston and offset of how the compass is placed

        # Ensure heading is 0-360
        if heading < 0:
            heading += 360
        elif heading > 360:
            heading -= 360

        compass.debug(f"Read compass: {heading}°")

        return heading

    def update_compass_thread(self):
        while True:
            states.heading = self.read_compass()

            sleep(.05)