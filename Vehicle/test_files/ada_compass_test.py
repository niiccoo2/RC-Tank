import time
import board
import adafruit_qmc5883p

i2c = board.I2C()

sensor = adafruit_qmc5883p.QMC5883P(i2c)

while True:
    mag_x, mag_y, mag_z = sensor.magnetic

    print(f"X:{mag_x:2.3f}, Y:{mag_y:2.3f}, Z:{mag_z:2.3f} G")
    print("")

    time.sleep(1)