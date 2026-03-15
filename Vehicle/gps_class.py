import serial # type: ignore
import time
from pydantic import BaseModel
import pynmea2

class GPSResponse(BaseModel):
    lat: float
    lon: float
    alt: float

class GPS:
    def __init__(self):
        print('Initializing GPS')
        self.port = serial.Serial("/dev/ttyACM0", baudrate=115200, timeout=1)
        time.sleep(.5)
        print('GPS Intitalized')
    
    def read_data(self):
        if not self.port:
            return GPSResponse(
                lat=0, lon=0, alt=0
            )
        
        try:
            while True:
                try:
                    line = self.port.readline().decode('ascii', errors='replace').strip()
                    if line.startswith('$GNGGA') or line.startswith('$GNRMC'):
                        msg = pynmea2.parse(line)

                        if isinstance(msg, pynmea2.GGA):
                            fix_quality = int(msg.gps_qual) if msg.gps_qual else 0
                            fix_label = {0: "No Fix", 1: "GPS", 4: "RTK Fixed", 5: "RTK Float"}.get(fix_quality, str(fix_quality))
                            #print(f"Lat: {msg.latitude}, Lon: {msg.longitude}, Fix: {fix_label}")


                            return GPSResponse(
                                lat=msg.latitude,
                                lon=msg.longitude,
                                alt=float(msg.altitude or 0.0)
                            )

                            if fix_quality == 4:
                                print("--- RTK FIXED (Centimeter Accuracy!) ---")

                except pynmea2.ParseError:
                    pass
                except (ValueError, IOError) as e:
                    print(f"Dropped packet: {e}")

        except KeyboardInterrupt:
            print("Stopping...")
        
        def __del__(self):
            self.close()

        # No valid GPS data found
        print("No GPS data found after reading multiple lines")
        return GPSResponse(
            lat=0, lon=0, alt=0
        )