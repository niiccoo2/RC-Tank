
import time
import sys
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

while True:
	(dataReady,dataOverflow,dataSkippedForReading) = compass.status()
	if (dataReady == 1):
		(x,y,z,rotX,rotY,rotZ) = compass.heading()
		print(f"Heading: rotX={rotX}° rotY={rotY}° rotZ={rotZ}° [x={x},y={y},z={z}], overflow={dataOverflow}, skip={dataSkippedForReading}, Temp={compass.getTemperature()}°C")
	time.sleep(0.5)