import board #type:ignore
import adafruit_qmc5883p #type:ignore

class Compass:
    def __init__(self):
        self.i2c = board.I2C()
        self.sensor = adafruit_qmc5883p.QMC5883P(self.i2c)
    
    def read_compass(self):
        return self.sensor.magnetic