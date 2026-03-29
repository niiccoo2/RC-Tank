#!/usr/bin/env python
# -*- coding: utf-8 -*-

# QMC5883L magnetic compass (for x,y,z axes) access

import smbus # type:ignore
import math
import sys

class QMC5883:

	#Register Addresses
	CONTROL_REG1_ADDR = 0x09
	CONTROL_REG2_ADDR = 0x0A
	STATUS_REG_ADDR = 0x06
	SET_RESET_PERIOD_REG_ADDR = 0x0B
	CHIP_ID_REG_ADDR = 0x0D
	DATA_REG_START_ADDR = 0x00
	DATA_REG_SIZE_BYTE = 6
	TEMP_REG_START_ADDR = 0x7
	TEMP_REG_SIZE_BYTE = 2

	#control register 1 - Addr 0x09
	#7	6	5	4	3	2	1	0
	#OSR[1:0]	RNG[1:0]	ODR[1:0]	MODE[1:0]
	#MODE
	MODE_CONTROL = {
		"Standby":    int('00',2),
		"Continuous": int('01',2)
	}

	#ODR
	OUTPUT_DATA_RATE = {
		"10Hz":  int('00',2),
		"50Hz":  int('01',2),
		"100Hz": int('10',2),
		"200Hz": int('11',2)
	}

	#RNG
	FULL_SCALE = {
		"2Gauss": int('00',2),
		"8Gauss": int('01',2)
	}

	#OSR - the higher the better, but the more power consumption
	OVER_SAMPLE_RATIO = {
		"512": int('00',2),
		"256": int('01',2),
		"128": int('10',2),
		"64" : int('11',2)
	}

	#Control register 2 - Addr 0x0A
	#7		6		5	4	3	2	1	0
	#SOFT_RST	ROL_PNT		-	-	-	-	-	INT_ENB
	#INT_EN
	INTERRUPT = {
		"DisableInt": 0,
		"EnableInt" : 1
	}

	#ROL_PNT
	POINTER_ROLL_OVER = {
		"DisableRollOver": 0,
		"EnableRollOver" : 1
	}

	#SOFT_RST
	SOFT_RESET = {
		"NoSoftReset"	: 0,
		"DoSoftReset"	: 1
	}

	#Set/Reset Period Regsiter - Addr 0x0B
	#Shall be set to 0x01
	SET_RESET_PERIOD = {
		"DefaultSetResetPeriod" : 0x01
	}

	def __init__(self, busNumber=1, deviceAddress=0x0d, mode="Continuous", sampleRate="200Hz",\
				 range="2Gauss", overSampleRatio="512", tempOffset=40, xOffset = 0,yOffset = 0,zOffset = 0):
		self.bus = smbus.SMBus(busNumber)
		self.address = deviceAddress
		self.tempOffset = tempOffset
		if (range == "2Gauss"):
			self.max_mag = 2.0
		else:
			self.max_mag = 8.0
		self.xOffset = xOffset
		self.yOffset = yOffset
		self.zOffset = zOffset
		self.ControlReg1 = (self.OVER_SAMPLE_RATIO[overSampleRatio] << 6) |\
						   (self.FULL_SCALE[range] << 4) |\
						   (self.OUTPUT_DATA_RATE[sampleRate] << 2) |\
						   (self.MODE_CONTROL[mode])
		#print bin(self.ControlReg1)

		self.ControlReg2 = (self.SOFT_RESET["NoSoftReset"] << 7) |\
						   (self.POINTER_ROLL_OVER["DisableRollOver"] << 6) |\
						   (int('00000',2) << 1) |\
						   (self.INTERRUPT["DisableInt"])
		#print bin(self.ControlReg2)

		self.PeriodRegister = 0x01
		self.bus.write_byte_data(self.address, self.CONTROL_REG1_ADDR, self.ControlReg1)
		self.bus.write_byte_data(self.address, self.CONTROL_REG2_ADDR, self.ControlReg2)
		self.bus.write_byte_data(self.address, self.SET_RESET_PERIOD_REG_ADDR, self.PeriodRegister)

	# gives the temperature in °C - Temperature is not calibrated - adapt "tempOffset" to adapt it to your environment
	def getTemperature(self):
		tempData = self.bus.read_i2c_block_data(self.address, self.TEMP_REG_START_ADDR, self.TEMP_REG_SIZE_BYTE)
		self.temperature = self.fromTwosComplement16(tempData[1] << 8 | tempData[0]) / 100 + self.tempOffset
		#print ("Temperature={}°C".format(self.temperature))
		return self.temperature

	# converts a 16bit value in twos complement into a signed integer
	def fromTwosComplement16(self, value):
		result = value
		# Convert twos compliment to integer
		if(value & (1 << 15)):
			# subtract one
			result = value - 1
			# negate the number and mask it to the given bit size
			result = (~result) & 0xFFFF
			# set the sign
			result = result * (-1)

		return result

	# converts 2 data bytes in twos complement into a signed 16 bit value
	def convert(self, data, offset):
		val = self.fromTwosComplement16(data[offset+1] << 8 | data[offset])
		return val

	# reads and gives the status bits of the chip
	# x,y,z data shall only be read if statusBit "dataReady" = 1
	def status(self):
		status = self.bus.read_byte_data(self.address, self.STATUS_REG_ADDR)
		dataReady = status & 0x01
		dataOverflow = (status & (1 << 1)) >> 1
		dataSkippedForReading = (status & (1 << 2)) >> 2
		return (dataReady,dataOverflow,dataSkippedForReading)

	# gives the "calibrated" axes measurement results
	def axes(self):
		data = self.bus.read_i2c_block_data(self.address, self.DATA_REG_START_ADDR, self.DATA_REG_SIZE_BYTE)
		#print map(hex, data)
		x = self.convert(data, 0) + self.xOffset
		y = self.convert(data, 2) + self.yOffset
		z = self.convert(data, 4) + self.zOffset
		#print("x={},y={},z={}".format(x,y,z))
		return(x,y,z)

	# gives the axes measurement results and the calculated rotation
	# rotZ is the rotation about the z axis: x-axis angle to north (z pointing up)
	# rotY is the rotation about the y axis: z-axis angle to north (y pointing up)
	# rotX is the rotation about the x axis: y-axis angle to north (x pointing up)
	def heading(self):
		(x, y, z) = self.axes()
		#todo: declination
		rotZ = self.rotation(x,y)
		rotY = self.rotation(z,x)
		rotX = self.rotation(y,z)
		return (x,y,z,rotX,rotY,rotZ)

	# calculates the rotation angle in degrees
	def rotation(self,adjacentSide, oppositeSide):
		rotationRad = math.atan2(oppositeSide, adjacentSide)
		# check for wrap and compensate
		if (rotationRad < 0):
			rotationRad += 2* math.pi
		elif (rotationRad > 2* math.pi):
			rotationRad -= 2 * math.pi

		#convert from radians to degree
		rotationDeg = rotationRad * 180 / math.pi
		return math.floor(rotationDeg)

	# collects the max of x,y,z and calculates the offset
	# call this method with QMC5883 xOffset,yOffset and zOffset = 0
	# requires the user to rotate the chip until no more changes in x,y,z and offset occur
	# has to be aborted with STRG+C
	# use the xOffset,yOffset,zOffset result for the initialization of the QMC5883
	def calibrate(self):
		xMin = 0
		xMax = 0
		yMin = 0
		yMax = 0
		zMin = 0
		zMax = 0
		xOffset = 0
		yOffset = 0
		zOffset = 0

		print ("Rotate your sensor in all directions until there are no longer changes in the reading. Stop with CTRL+C. Use the given x,y,z Offsets for QMC initialization")

		while True:
			(dataReady,overFlow,skip) = self.status()
			if (dataReady):
				(x,y,z) = self.axes()
				if (x < xMin):
					xMin = x
				if (x > xMax):
					xMax = x
				if (y < yMin):
					yMin = y
				if (y > yMax):
					yMax = y
				if (z < zMin):
					zMin = z
				if (z > zMax):
					zMax = z
				xOffset = ((xMax - xMin) / 2) - xMax
				yOffset = ((yMax - yMin) / 2) - yMax
				zOffset = ((zMax - zMin) / 2) - zMax

				sys.stdout.write("\rxMin[{}],xMax[{}],xOffset[{}],yMin[{}],yMax[{}],yOffset[{}],zMin[{}],zMax[{}],zOffset[{}]".format(xMin,xMax,xOffset,yMin,yMax,yOffset,zMin,zMax,zOffset))
				sys.stdout.flush()
