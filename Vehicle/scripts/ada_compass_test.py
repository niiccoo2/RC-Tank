import time
import board #type:ignore
import adafruit_qmc5883p #type:ignore
import math

i2c = board.I2C()

sensor = adafruit_qmc5883p.QMC5883P(i2c)

while True:
    mag_x, mag_y, mag_z = sensor.magnetic

    print(f"X:{mag_x:2.3f}, Y:{mag_y:2.3f}, Z:{mag_z:2.3f} G")

    heading = math.atan2(mag_y, mag_x)*(180/math.pi)
    print(heading)

    print("")

    time.sleep(1)