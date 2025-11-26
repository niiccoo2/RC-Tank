#!/usr/bin/env python3
"""
hover_rpi.py
Send hoverboard (steer, speed, state) packets from a Raspberry Pi Zero 2 W via UART.

Packet layout (little-endian):
  uint16 start   = 0xCDAB
  int16  steer
  int16  speed
  uint16 state
  uint16 crc     = sum(all previous bytes) & 0xFFFF
"""

import struct
import time
import serial # type: ignore
import sys

# ----------------------
# Config
# ----------------------
PORT = "/dev/serial0"       # change to /dev/ttyUSB0 if using USB-serial adapter
BAUDRATE = 19200
SEND_MS = 50                # send interval in milliseconds
START_WORD = 0xCDAB

# ----------------------
# Serial open
# ----------------------
def open_serial(port=PORT, baud=BAUDRATE, timeout=0.1):
    try:
        ser = serial.Serial(port, baudrate=baud, timeout=timeout)
        # flush input/output
        ser.reset_input_buffer()
        ser.reset_output_buffer()
        return ser
    except Exception as e:
        print(f"Failed to open serial port {port}: {e}", file=sys.stderr)
        raise

# ----------------------
# Build & send packet
# ----------------------
def build_packet(steer: int, speed: int, state: int = 1) -> bytes:
    """
    Build the hoverboard packet (without CRC), compute CRC (sum of bytes),
    and return the full bytes to send.
    steer/speed are signed 16-bit. state is unsigned 16-bit.
    """
    # pack start, steer, speed, state (little-endian)
    # '<' = little-endian; H = uint16, h = int16
    msg = struct.pack("<HhhH", START_WORD, int(steer) & 0xFFFF, int(speed) & 0xFFFF, int(state) & 0xFFFF)

    # compute CRC as sum of bytes of msg modulo 65536
    # must treat msg as sequence of unsigned bytes
    crc = sum(msg) & 0xFFFF

    full = msg + struct.pack("<H", crc)
    return full

def send_hover(ser: serial.Serial, steer: int, speed: int, state: int = 1) -> None:
    packet = build_packet(steer, speed, state)
    ser.write(packet)
    # optional: flush to ensure immediate send
    ser.flush()

# ----------------------
# Simple demo loop
# ----------------------
def demo_loop(port=PORT, baud=BAUDRATE, send_ms=SEND_MS):
    ser = open_serial(port, baud)
    print(f"Opened {port} @ {baud} bps. Sending every {send_ms} ms. Ctrl-C to stop.")

    try:
        t_next = time.monotonic()
        iMax = 500
        iPeriod = 3.0
        while True:
            now = time.monotonic()

            # simple triangular-ish speed pattern similar to original
            # keep values in signed 16-bit range
            # note: integer math for steer/speed
            fScaleMax = 1.6 * (max(3, min(int(iPeriod), 9)) / 9.0)
            # use a repeating saw/triangle based on monotonic time
            # period scaling to create variation
            pseudo = int((now / iPeriod + 250)) % 1000
            iSpeed = int((fScaleMax * iMax / 100.0) * (abs(pseudo - 500) - 250))
            iSpeed = max(-iMax, min(iMax, iSpeed))

            pseudo2 = int((now / 0.4 + 100)) % 400
            iSteer = int(abs(pseudo2 - 200) - 100)

            # state: keep default 1 (ledGreen) unless you want to toggle
            send_hover(ser, iSteer, iSpeed, state=1)

            # wait for next
            t_next += send_ms / 1000.0
            sleep_for = t_next - time.monotonic()
            if sleep_for > 0:
                time.sleep(sleep_for)
            else:
                # if we're behind, don't block (prevents drift)
                t_next = time.monotonic()
    except KeyboardInterrupt:
        print("\nStopped by user.")
    finally:
        ser.close()
        print("Serial closed.")


# ----------------------
# Helper CLI to send single commands
# ----------------------
def cli_send_once(port=PORT, baud=BAUDRATE, steer=0, speed=0, state=1):
    ser = open_serial(port, baud, timeout=1)
    try:
        print(f"Sending steer={steer}, speed={speed}, state={state}")
        send_hover(ser, steer, speed, state)
    finally:
        ser.close()

# ----------------------
# Entry point
# ----------------------
if __name__ == "__main__":
    # Simple CLI:
    #   python3 hover_rpi.py            -> demo loop
    #   python3 hover_rpi.py once s p  -> send once (s=steer, p=speed)
    args = sys.argv[1:]
    if len(args) >= 1 and args[0].lower() == "once":
        s = int(args[1]) if len(args) >= 2 else 0
        p = int(args[2]) if len(args) >= 3 else 0
        st = int(args[3]) if len(args) >= 4 else 1
        cli_send_once(PORT, BAUDRATE, s, p, st)
    else:
        demo_loop(PORT, BAUDRATE, SEND_MS)
