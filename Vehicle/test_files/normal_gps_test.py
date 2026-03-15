import serial
import pynmea2 # type:ignore
import time

def run():
    port = serial.Serial("/dev/ttyACM0", baudrate=115200, timeout=1)

    print("Waiting for fix...")
    try:
        while True:
            try:
                line = port.readline().decode('ascii', errors='replace').strip()
                if line.startswith('$GNGGA') or line.startswith('$GNRMC'):
                    msg = pynmea2.parse(line)

                    if isinstance(msg, pynmea2.GGA):
                        fix_quality = int(msg.gps_qual) if msg.gps_qual else 0
                        fix_label = {0: "No Fix", 1: "GPS", 4: "RTK Fixed", 5: "RTK Float"}.get(fix_quality, str(fix_quality))
                        print(f"Lat: {msg.latitude}, Lon: {msg.longitude}, Fix: {fix_label}")
                        if fix_quality == 4:
                            print("--- RTK FIXED (Centimeter Accuracy!) ---")

            except pynmea2.ParseError:
                pass
            except (ValueError, IOError) as e:
                print(f"Dropped packet: {e}")

    except KeyboardInterrupt:
        print("Stopping...")
    finally:
        port.close()

if __name__ == '__main__':
    run()