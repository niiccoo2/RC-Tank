import serial
import base64
import socket
from ublox_gps import UbloxGps
from pygnssutils import GNSSNTRIPClient
import threading
import time
import os
from dotenv import load_dotenv

load_dotenv()

print(f"Read username: {os.getenv('NTRIP_USER')}")
print(f"Password length: {len(os.getenv('NTRIP_PWD') or '')} characters")

NTRIP_USER = os.getenv("NTRIP_USER")
NTRIP_PWD = os.getenv("NTRIP_PWD")
NTRIP_SERVER = "macorsrtk.massdot.state.ma.us" 
NTRIP_PORT = 10000
MOUNTPOINT = "RTCM3MSM_IMAX"
# MOUNTPOINT = "RTCM3_NEAR"
GGA_INTERVAL_S = 2


def preflight_ntrip_mountpoint():
    """Quick raw NTRIP request to show caster status and header details."""
    try:
        auth = base64.b64encode(f"{NTRIP_USER}:{NTRIP_PWD}".encode()).decode()
        request = (
            f"GET /{MOUNTPOINT} HTTP/1.0\r\n"
            f"Host: {NTRIP_SERVER}:{NTRIP_PORT}\r\n"
            "User-Agent: NTRIP RC-Tank/1.0\r\n"
            f"Authorization: Basic {auth}\r\n"
            "Connection: close\r\n"
            "\r\n"
        )

        with socket.create_connection((NTRIP_SERVER, NTRIP_PORT), timeout=8) as sock:
            sock.settimeout(8)
            sock.sendall(request.encode())
            raw = sock.recv(1024)
            text = raw.decode(errors="replace")
            header, _, body = text.partition("\r\n\r\n")
            first_line = header.splitlines()[0] if header else "<no response>" # type: ignore
            print(f"NTRIP preflight: {first_line}")
            if header:
                print("NTRIP headers:")
                for line in header.splitlines()[1:8]:
                    print(f"  {line}")
            if body:
                preview = body[:80].replace("\r", " ").replace("\n", " ")
                print(f"NTRIP body preview: {preview}")

            lower_blob = (header + "\n" + body).lower()
            banned = "banned your ip" in lower_blob or "forbidden" in lower_blob
            ok = "200" in first_line or "icy" in first_line.lower()
            return {
                "ok": ok,
                "banned": banned,
                "first_line": first_line,
            }
    except Exception as err:
        print(f"NTRIP preflight failed: {err}")
        return {
            "ok": False,
            "banned": False,
            "first_line": str(err),
        }

def feed_rtcm(port, stop_event, ref_lat, ref_lon):
    """Background task to feed RTCM corrections into the GPS serial port"""
    retry_delay_s = 15
    retries = 0
    max_retries = 6
    while not stop_event.is_set():
        if retries >= max_retries:
            print("NTRIP stopped after max retries to avoid caster spam.")
            break
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
                    "version": "1.0",
                    "ggamode": 1,
                    "ggainterval": GGA_INTERVAL_S,
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
            retry_delay_s = 15
            retries = 0
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
            retry_delay_s = min(retry_delay_s * 2, 120)
            retries += 1
        except Exception as err:
            if stop_event.is_set():
                break
            print(f"NTRIP error, reconnecting: {err}")
            time.sleep(retry_delay_s)
            retry_delay_s = min(retry_delay_s * 2, 120)
            retries += 1

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

    print(f"NTRIP GGA enabled: interval={GGA_INTERVAL_S}s, ref=({ref_lat}, {ref_lon})")
    preflight = preflight_ntrip_mountpoint()
    if preflight.get("banned"):
        print("Caster reported IP ban. Not starting NTRIP stream to avoid extending ban.")
        print("Wait for ban timeout or use a different network IP/mountpoint.")
        port.close()
        return
    if not preflight.get("ok"):
        print("NTRIP preflight did not return a stream-OK status. Not starting stream.")
        port.close()
        return

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
