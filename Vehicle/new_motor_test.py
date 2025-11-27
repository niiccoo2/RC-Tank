#!/usr/bin/env python3
import struct
import serial  # type: ignore
import time

# ----------------------
# Config (mirror Arduino)
# ----------------------
PORT = "/dev/serial0"  # or COM port on Windows
BAUDRATE = 19200
SEND_MILLIS = 100
SLAVES = [0, 1]  # hoverboard IDs
iMax = 500
iPeriod = 3.0

HEADER = b'NW'
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
    """Simple sum CRC, 16-bit"""
    return sum(data) & 0xFFFF

def build_packet(slave_id: int, steer: int, speed: int, state: int = 1) -> bytes:
    """Build packet exactly like Arduino format"""
    # Clamp values to int16 for steer & speed
    steer = max(-32768, min(32767, steer))
    speed = max(-32768, min(32767, speed))
    state = state & 0xFFFF

    payload = struct.pack("<hhH", steer, speed, state)  # 6 bytes
    length = len(payload)
    packet_no_crc = HEADER + bytes([slave_id, CMD_SET_SPEED, length]) + payload
    crc = calc_crc(packet_no_crc)
    return packet_no_crc + struct.pack("<H", crc)

def send_to_slave(ser, slave_id, steer, speed, state=1):
    packet = build_packet(slave_id, steer, speed, state)
    ser.write(packet)
    ser.flush()

# ----------------------
# Main loop (mirror Arduino)
# ----------------------
def demo_loop():
    ser = open_serial(PORT, BAUDRATE)
    print(f"Opened {PORT} @ {BAUDRATE} bps. Ctrl-C to stop.")

    send_index = 0
    t_next = time.monotonic()

    try:
        while True:
            now = time.monotonic()

            # --- Calculate speed and steer exactly like Arduino ---
            pseudo_speed = int(now / iPeriod + 250) % 1000
            iSpeed = int((1.6 * iMax / 100.0) * (abs(pseudo_speed - 500) - 250))
            iSpeed = max(-iMax, min(iMax, iSpeed))

            pseudo_steer = int(now / 0.4 + 100) % 400
            iSteer = int(abs(pseudo_steer - 200) - 100)

            # --- Rotate through slaves and alternate sending ---
            slave_id = SLAVES[send_index % len(SLAVES)]
            if send_index % 2 == 0:
                send_to_slave(ser, slave_id, iSpeed + iSteer, iSpeed + iSteer, state=1)
            else:
                send_to_slave(ser, slave_id, -iSpeed + iSteer, -iSpeed + iSteer, state=1)

            send_index += 1

            # --- Wait until next send ---
            t_next += SEND_MILLIS / 1000.0
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
# Entry point
# ----------------------
if __name__ == "__main__":
    demo_loop()
