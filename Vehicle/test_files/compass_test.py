
import math
import time
from qmc5883 import QMC5883

#initialize with the offsets read with example.getCalibration.py
#example output:
#xMin[-5510],xMax[5740],xOffset[-115],yMin[-8215],yMax[2977],yOffset[2619],zMin[-5610],zMax[5025],zOffset[292]
compass = QMC5883(
    busNumber=7,
    deviceAddress=0x2c,
    xOffset=0,
    yOffset=0,
    zOffset=0
)

print("Done with init")

while True:
	try:
		x, y, z = compass.axes()
		heading = (math.degrees(math.atan2(y, x)) + 360.0) % 360.0
		temp_c = compass.getTemperature()
		print(f"Heading={heading:6.1f} deg | x={x:6.0f} y={y:6.0f} z={z:6.0f} | temp={temp_c:5.1f} C")
	except Exception as e:
		print(f"Read failed: {e}")

	time.sleep(0.2)