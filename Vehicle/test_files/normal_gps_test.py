import serial
import base64
import socket
from ublox_gps import UbloxGps
import threading
import time

def run():
    gps_port = "/dev/ttyACM0"
    print(f"Using GPS port: {gps_port}")
    port = serial.Serial(gps_port, baudrate=38400, timeout=1)
    gps = UbloxGps(port)
    stop_event = threading.Event()

    # Grab one valid position to seed fixed-reference GGA for NTRIP caster.
    ref_lat = None
    ref_lon = None
    for _ in range(150):
        try:
            seed = gps.geo_coords()
            if seed:
                ref_lat = seed.lat
                ref_lon = seed.lon
                break
        except (ValueError, IOError):
            pass
        time.sleep(0.2)

    if ref_lat is None or ref_lon is None:
        print("No valid GNSS fix yet, cannot start NTRIP with GGA enabled.")
        print("Move antenna to open sky and restart.")
        port.close()
        return
    
    try: 
        while True:
            try: 
                coords = gps.geo_coords()
                # NAV-PVT message tells us the 'fix' type:
                # 3 = 3D Fix, 4 = RTK Fixed (1cm), 5 = RTK Float (decimeters)
                if coords:
                    print(f"Lat: {coords.lat}, Lon: {coords.lon}, FixType: {coords.fixType}")
                
                    if coords.fixType == 4:
                        print("--- RTK FIXED (Centimeter Accuracy!) ---")
                
            except (ValueError, IOError):
                print("Dropped packets") # Ignore occasional dropped packets
                
    except KeyboardInterrupt:
        print("Stopping...")
    finally:
        stop_event.set()
        port.close()

if __name__ == '__main__':
    run()
