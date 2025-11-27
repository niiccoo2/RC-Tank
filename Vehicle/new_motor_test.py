#!/usr/bin/env python3
import struct
import serial  # type: ignore
import time

# ----------------------
# Config
# ----------------------
PORT = "/dev/serial0"  # or COM port on Windows
BAUDRATE = 19200
SEND_INTERVAL = 0.1  # seconds between packets

iMax = 500
iPeriod = 3.0

# Packet constants (from INO raw data)
HEADER = b'\x0C\xFE'
CMD_SET_SPEED = 0x01

# ----------------------
# Serial helpers
# ----------------------
def open_serial(port=PORT, baud=BAUDRATE):
    ser = serial.Serial(port, baudrate=baud, timeout=0.1)
    ser.reset_input_buffer()
    ser.reset_output_buffer()
    return ser

def calc_crc(data: bytes) -> int:
    """Simple CRC as sum of bytes modulo 65536 (matching INO)"""
    return sum(data) & 0xFFFF

def build_packet(steer: int, speed: int, state: int = 1) -> bytes:
    """
    Build a hoverboard packet similar to Arduino.
    Packet structure (from INO observation):
    [HEADER(2)][CMD(1)][??(2)][payload(6)][CRC(2)]
    Payload = steer(int16), speed(int16), state(uint16)
    """
    steer = max(-32768, min(32767, steer))
    speed = max(-32768, min(32767, speed))
    state = state & 0xFFFF

    payload = struct.pack("<hhH", steer, speed, state)
    # Two unknown bytes between CMD and payload (observed as 0x01 0x00)
    middle_bytes = b'\x01\x00'
    packet_no_crc = HEADER + bytes([CMD_SET_SPEED]) + middle_bytes + payload
    crc = calc_crc(packet_no_crc)
    packet = packet_no_crc + struct.pack("<H", crc)
    return packet

def send_packet(ser, steer: int, speed: int, state: int = 1):
    packet = build_packet(steer, speed, state)
    ser.write(packet)
    ser.flush()

# ----------------------
# Main loop
# ----------------------
def demo_loop():
    ser = open_serial(PORT, BAUDRATE)
    print(f"Opened {PORT} @ {BAUDRATE} bps. Ctrl-C to stop.")

    try:
        while True:
            now = time.monotonic()

            # --- Generate pseudo speed/steer like Arduino ---
            pseudo_speed = int(now / iPeriod + 250) % 1000
            iSpeed = int((1.6 * iMax / 100.0) * (abs(pseudo_speed - 500) - 250))
            iSpeed = max(-iMax, min(iMax, iSpeed))

            pseudo_steer = int(now / 0.4 + 100) % 400
            iSteer = int(abs(pseudo_steer - 200) - 100)

            # Alternate direction
            if int(now / SEND_INTERVAL) % 2 == 0:
                send_packet(ser, iSteer, iSpeed, state=1)
            else:
                send_packet(ser, -iSteer, -iSpeed, state=1)

            time.sleep(SEND_INTERVAL)

    except KeyboardInterrupt:
        print("\nStopped by user.")
    finally:
        ser.close()
        print("Serial closed.")

# ----------------------
# Entry point
# ----------------------
if __name__ == "__main__":
    demo_loop()
