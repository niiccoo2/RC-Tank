import time
import board #type:ignore
import adafruit_qmc5883p #type:ignore
import math

i2c = board.I2C()

sensor = adafruit_qmc5883p.QMC5883P(i2c)

# while True:
#     mag_x, mag_y, mag_z = sensor.magnetic

#     print(f"X:{mag_x:2.3f}, Y:{mag_y:2.3f}, Z:{mag_z:2.3f} G")

#     heading = math.atan2(mag_y, mag_x)*(180/math.pi)
#     if heading < 0:
#         heading = heading+360
#     print(heading)

#     print("")

#     time.sleep(1)


# mag_x, mag_y, mag_z = [], [], []

# print("Rotate the sensor in all directions for 30 seconds...")
# start_time = time.time()
# while time.time() - start_time < 30:
#     x, y, z = sensor.magnetic
#     mag_x.append(x)
#     mag_y.append(y)
#     mag_z.append(z)
#     time.sleep(0.1)

# offset_x = (max(mag_x) + min(mag_x)) / 2
# offset_y = (max(mag_y) + min(mag_y)) / 2
# offset_z = (max(mag_z) + min(mag_z)) / 2

# avg_delta_x = (max(mag_x) - min(mag_x)) / 2
# avg_delta_y = (max(mag_y) - min(mag_y)) / 2
# avg_delta_z = (max(mag_z) - min(mag_z)) / 2

# avg_delta = (avg_delta_x + avg_delta_y + avg_delta_z) / 3

# scale_x = avg_delta / avg_delta_x
# scale_y = avg_delta / avg_delta_y

# print(f"offset_x: {offset_x}, offset_y: {offset_y}, scale_x: {scale_x}, scale_y: {scale_y}")

OFFSET_X = -0.198
OFFSET_Y = 0.013
SCALE_X = 0.84  # Average of two runs
SCALE_Y = 0.73  # Average of two runs

def get_heading():
    raw_x, raw_y, raw_z = sensor.magnetic
    
    # Apply calibration
    cal_x = (raw_x - OFFSET_X) * SCALE_X
    cal_y = (raw_y - OFFSET_Y) * SCALE_Y
    
    # Calculate angle in radians, then convert to degrees
    heading = math.atan2(cal_x, cal_y) * (180 / math.pi)
    
    heading = heading-13.75-90  # that is the magnetic difference for boston and offset of how the compass is placed

    # Ensure heading is 0-360
    if heading < 0:
        heading += 360

    return heading

# user = input("Read heading? (Y/n): ").lower()

# if user == 'y' or user == '':
while True:
    print(get_heading())