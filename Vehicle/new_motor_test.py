#!/usr/bin/env python3
import struct
import serial  # type: ignore
import time

# ----------------------
# Config
# ----------------------
PORT = "/dev/serial0"  # or use the appropriate serial port (e.g., COMx on Windows)
BAUDRATE = 19200
SEND_INTERVAL = 0.05  # 50ms, matching Arduino SEND_MILLIS
SPEED = 500  # Constant speed for motors
STATE = 1  # Enabled

# Header matches Arduino implementation
HEADER = b'\xFF\xFF'

# ----------------------
# Helper Functions
# ----------------------
def calc_crc(data: bytes) -> int:
    """Calculate CRC (matching Arduino CalculateCRC function)."""
    crc = 0xFFFF
    for byte in data:
        crc ^= byte << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ 0x1021
            else:
                crc <<= 1
            crc &= 0xFFFF  # Keep CRC 16-bit
    return crc

def build_packet(slave_id: int, speed: int, state: int) -> bytes:
    """
    Builds a packet equivalent to HoverSendDebug in Arduino.
    Packet = [HEADER(2)][SlaveID(1)][Speed(int16)][State(uint8)][CRC(uint16)]
    """
    # Ensure values are within limits
    speed = max(-32768, min(32767, speed))
    state = state & 0xFF

    # Build packet excluding CRC
    packet_no_crc = HEADER + bytes([slave_id]) + struct.pack("<hB", speed, state)
    crc = calc_crc(packet_no_crc)
    packet = packet_no_crc + struct.pack("<H", crc)  # Append CRC as uint16
    return packet

def send_packet(ser, slave_id: int, speed: int, state: int):
    """Send a packet to the hoverboard."""
    packet = build_packet(slave_id, speed, state)
    ser.write(packet)
    ser.flush()

    # Debug: Print the packet
    print(f"Sent packet to Slave {slave_id}: {packet.hex()}")

# ----------------------
# Main Loop
# ----------------------
def demo_loop():
    ser = serial.Serial(PORT, baudrate=BAUDRATE, timeout=1)
    print(f"Opened {PORT} @ {BAUDRATE} bps. Ctrl-C to stop.")

    try:
        while True:
            # Send to slave 0 (left motor)
            send_packet(ser, slave_id=0, speed=SPEED, state=STATE)

            # Send to slave 1 (right motor)
            send_packet(ser, slave_id=1, speed=SPEED, state=STATE)

            time.sleep(SEND_INTERVAL)  # Wait for the next frame
    except KeyboardInterrupt:
        print("\nStopped by user.")
    finally:
        ser.close()
        print("Serial closed.")

# ----------------------
# Entry Point
# ----------------------
if __name__ == "__main__":
    demo_loop()