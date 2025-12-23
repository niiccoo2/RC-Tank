import serial # type: ignore
import time
from pydantic import BaseModel

class GPSResponse(BaseModel):
    lat: float
    lon: float
    date: str
    utc: str
    alt: float
    speed: float
    course: float

class GPS:
    def __init__(self):
        self.ser = serial.Serial('/dev/ttyUSB3', 115200, timeout=1)
        time.sleep(.5)

        self.ser.write(b'AT+CGPS=1,1\r')
    
    def read_data(self):
        if not self.ser:
            return
        
        response = GPSResponse
        
        self.ser.write(b'AT+CGPSINFO\r')
        
        line = self.ser.readline()
        msg = line.decode(errors='ignore').strip()

        fields = msg.replace("+CGPSINFO: ", "").split(",")

        lat_raw, ns, lon_raw, ew, date, utc_time, altitude, speed, course = fields

        # Convert latitude and longitude from degrees+minutes to decimal degrees
        lat_deg = float(lat_raw[:2]) + float(lat_raw[2:])/60
        if ns == "S":
            lat_deg = -lat_deg

        lon_deg = float(lon_raw[:3]) + float(lon_raw[3:])/60
        if ew == "W":
            lon_deg = -lon_deg

        # Convert other values to floats
        altitude = float(altitude)
        speed = float(speed)
        course = float(course)

        response.lat = lat_deg
        response.lon = lon_deg
        response.date = date
        response.utc = utc_time
        response.alt = altitude
        response.speed = speed
        response.course = course

        return response