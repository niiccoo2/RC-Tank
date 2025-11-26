#!/usr/bin/env python3
"""
RemoteUARTBus Python3 client for Raspberry Pi Zero 2 W
Sends commands to multiple hoverboards on the same bus.

Packet format (simplified, matches hoverboard firmware RemoteUARTBus):
[HEADER 0x4E 0x57 "NW"]
[SLAVE_ID] (0-3)
[COMMAND_ID] (0x01=set speed/steer)
[LENGTH] (payload length)
[STEER_L STEER_H SPEED_L SPEED_H STATE_L STATE_H]
[CRC_L CRC_H]
"""

import struct
import serial # type: ignore
import time
import sys

# ----------------------
# Config
# ----------------------
PORT = "/dev/serial0"
BAUDRATE = 19200
SEND_MS = 100
SLAVES = [0]

HEADER = b'NW'
CMD_SET_SPEED = 0x01

# ----------------------
# Serial
# ----------------------
def open_serial(port=PORT, baud=BAUDRATE):
    ser = serial.Serial(port, baudrate=baud, timeout=0.1)
    ser.reset_input_buffer()
    ser.reset_output_buffer()
    return ser

# ----------------------
# CRC helper
# ----------------------
def calc_crc(data: bytes) -> int:
    return sum(data) & 0xFFFF

# ----------------------
# Build packet for bus
# ----------------------
def build_packet(slave_id, steer, speed, state=1):
    # clamp values
    steer = max(-32768, min(32767, steer))
    speed = max(-32768, min(32767, speed))
    state = state & 0xFFFF  # still unsigned

    payload = struct.pack("<hhH", steer, speed, state)
    # build your full packet with headers/checksum as needed
    return payload


# ----------------------
# Send command to a single slave
# ----------------------
def send_to_slave(ser, slave_id, steer, speed, state=1):
    packet = build_packet(slave_id, steer, speed, state)
    ser.write(packet)
    ser.flush()

# ----------------------
# Demo loop
# ----------------------
def demo_loop():
    ser = open_serial(PORT, BAUDRATE)
    print(f"Opened {PORT} @ {BAUDRATE} bps. Ctrl-C to stop.")

    iMax = 500
    iPeriod = 3.0
    try:
        t_next = time.monotonic()
        while True:
            now = time.monotonic()
            fScaleMax = 1.6 * (max(3, min(int(iPeriod), 9)) / 9.0)
            pseudo = int((now / iPeriod + 250)) % 1000
            iSpeed = int((fScaleMax * iMax / 100.0) * (abs(pseudo - 500) - 250))
            iSpeed = max(-iMax, min(iMax, iSpeed))
            pseudo2 = int((now / 0.4 + 100)) % 400
            iSteer = int(abs(pseudo2 - 200) - 100)

            # send to all slaves
            for slave_id in SLAVES:
                send_to_slave(ser, slave_id, iSteer, iSpeed, state=1)

            # wait for next
            t_next += SEND_MS / 1000.0
            sleep_for = t_next - time.monotonic()
            if sleep_for > 0:
                time.sleep(sleep_for)
            else:
                t_next = time.monotonic()

    except KeyboardInterrupt:
        print("\nStopped by user.")
    finally:
        ser.close()
        print("Serial closed.")

# ----------------------
# CLI single command
# ----------------------
def cli_send_once(slave_id=0, steer=0, speed=0, state=1):
    ser = open_serial(PORT, BAUDRATE)
    try:
        send_to_slave(ser, slave_id, steer, speed, state)
        print(f"Sent steer={steer}, speed={speed} to slave {slave_id}")
    finally:
        ser.close()

# ----------------------
# Entry point
# ----------------------
if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) >= 1 and args[0].lower() == "once":
        sid = int(args[1]) if len(args) >= 2 else 0
        s = int(args[2]) if len(args) >= 3 else 0
        p = int(args[3]) if len(args) >= 4 else 0
        st = int(args[4]) if len(args) >= 5 else 1
        cli_send_once(sid, s, p, st)
    else:
        demo_loop()
