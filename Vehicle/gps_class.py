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
        print('Initializing GPS')
        self.ser = serial.Serial('/dev/ttyUSB3', 115200, timeout=1)
        time.sleep(.5)

        self.ser.write(b'AT+CGPS=1,1\r')
        print('GPS Intitalized')
    
    def read_data(self):
        if not self.ser:
            return GPSResponse(
                lat=0, lon=0, date="", utc="", alt=0, speed=0, course=0
            )
        
        # Clear any pending data
        self.ser.reset_input_buffer()
        
        self.ser.write(b'AT+CGPSINFO\r')
        
        # Read multiple lines to get past echo and find GPS data
        for _ in range(5):  # Try up to 5 lines
            line = self.ser.readline()
            msg = line.decode(errors='ignore').strip()
            
            # Skip empty lines and command echo
            if not msg or msg == "AT+CGPSINFO" or msg == "OK":
                continue
                
            # Found GPS data line
            if "+CGPSINFO:" in msg:
                fields = msg.replace("+CGPSINFO: ", "").split(",")
                
                # Check if we have enough fields
                if len(fields) < 9:
                    print(f"Not enough GPS fields: {fields}")
                    return GPSResponse(
                        lat=0, lon=0, date="", utc="", alt=0, speed=0, course=0
                    )

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

                return GPSResponse(
                    lat=lat_deg,
                    lon=lon_deg,
                    date=date,
                    utc=utc_time,
                    alt=altitude,
                    speed=speed,
                    course=course
                )
        
        # No valid GPS data found
        print("No GPS data found after reading multiple lines")
        return GPSResponse(
            lat=0, lon=0, date="", utc="", alt=0, speed=0, course=0
        )