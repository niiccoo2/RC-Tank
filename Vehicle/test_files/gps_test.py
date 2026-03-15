import serial
import sys
import types
import os

# ublox_gps imports spidev unconditionally, but spidev is Linux-only.
# Provide a minimal stub so this script runs on Windows with UART GPS.
if sys.platform.startswith("win"):
    spidev_stub = types.ModuleType("spidev")

    class _DummySpiDev:
        def __init__(self, *args, **kwargs):
            raise RuntimeError("spidev is not available on Windows")

    setattr(spidev_stub, "SpiDev", _DummySpiDev)
    sys.modules.setdefault("spidev", spidev_stub)

from ublox_gps import UbloxGps
from pygnssutils import GNSSNTRIPClient
import threading
import time

NTRIP_USER = "rtk@a.nicosmith.net"
NTRIP_PWD = "none"
NTRIP_SERVER = "rtk2go.com" 
NTRIP_PORT = 2101
# MOUNTPOINT = "Lowell_MA"
MOUNTPOINT = "Ellsworth202Grant"


def resolve_gps_port():
    """Resolve a usable GPS serial port for current platform."""
    env_port = os.getenv("GPS_PORT")
    if env_port:
        return env_port

    if sys.platform.startswith("win"):
        return "COM9"

    candidates = [
        "/dev/ttyACM0",
        "/dev/ttyTHS1",
        "/dev/ttyTHS2",
        "/dev/ttyUSB0",
    ]
    for dev in candidates:
        if os.path.exists(dev):
            return dev

    # Fall back to common Jetson UART if no candidate is visible yet.
    return "/dev/ttyTHS1"

def feed_rtcm(port, stop_event, ref_lat, ref_lon):
    """Background task to feed RTCM corrections into the GPS serial port"""
    retry_delay_s = 2
    while not stop_event.is_set():
        try:
            with GNSSNTRIPClient() as gnc:
                # Start NTRIP client and keep it alive until stop/reconnect.
                run_args = {
                    "server": NTRIP_SERVER,
                    "port": NTRIP_PORT,
                    "mountpoint": MOUNTPOINT,
                    "ntripuser": NTRIP_USER,
                    "ntrippassword": NTRIP_PWD,
                    "datatype": "RTCM",
                    "version": "2.0",
                    "ggamode": 1,
                    "ggainterval": 10,
                    "reflat": ref_lat,
                    "reflon": ref_lon,
                    "refalt": 0.0,
                    "refsep": 0.0,
                    "output": port,
                    "stopevent": stop_event,
                }

                gnc.run(**run_args)
                while gnc.connected and not stop_event.is_set():
                    time.sleep(0.5)
            retry_delay_s = 2
        except KeyError as err:
            if stop_event.is_set():
                break

            # pygnssutils may raise KeyError('code') if the caster reply is not
            # the expected NTRIP response shape.
            if str(err).strip("'\"") == "code":
                print(
                    "NTRIP response missing 'code'. Check mountpoint/user/password "
                    "or verify caster is returning a valid NTRIP stream."
                )
            else:
                print(f"NTRIP key error, reconnecting: {err}")

            time.sleep(retry_delay_s)
            retry_delay_s = min(retry_delay_s * 2, 15)
        except Exception as err:
            if stop_event.is_set():
                break
            print(f"NTRIP error, reconnecting: {err}")
            time.sleep(2)

def run():
    gps_port = resolve_gps_port()
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

    print(f"NTRIP GGA enabled: interval=10s, ref=({ref_lat}, {ref_lon})")

    # Start the NTRIP client in a separate thread
    ntrip_thread = threading.Thread(
        target=feed_rtcm,
        args=(port, stop_event, ref_lat, ref_lon),
        daemon=True,
    )
    ntrip_thread.start()

    print("Waiting for RTK Fix... (Ensure antenna is outside)")
    
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
                pass # Ignore occasional dropped packets
                
    except KeyboardInterrupt:
        print("Stopping...")
    finally:
        stop_event.set()
        ntrip_thread.join(timeout=2)
        port.close()

if __name__ == '__main__':
    run()
