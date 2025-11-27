#!/usr/bin/env python3
import struct
import serial  # type: ignore
import time

# ----------------------
# Configuration
# ----------------------
PORT = "/dev/serial0"  # Adjust as necessary (e.g., COMx on Windows)
BAUDRATE = 19200  # Matches Arduino setup
SEND_INTERVAL = 0.05  # Send commands every 50ms
SPEED = 500  # Constant motor speed
STATE = 1  # Enabled state

# ----------------------
# Utilities
# ----------------------
def calc_crc(data: bytes) -> int:
    """Calculate CRC (matching Arduino's CalcCRC function)."""
    crc = 0
    for byte in data:
        crc ^= (byte << 8)
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ 0x1021
            else:
                crc <<= 1
    return crc & 0xFFFF  # Ensure 16-bit CRC

def build_packet(slave_id: int, speed: int, state: int = STATE) -> bytes:
    """
    Build a hoverboard packet matching observed structure:
    Dynamic byte + Start Byte + Slave ID + Speed + State + CRC
    """
    # Ensure values fit within expected ranges
    speed = max(-1000, min(1000, speed))  # Clamp speed to [-1000, 1000]
    state = state & 0xFF  # Ensure state is an 8-bit value

    # Packet fields
    dynamic_byte = b'\xE3'  # Dynamic byte observed in the working data
    start_byte = b'\x2F'   # Start byte ('/')
    payload = struct.pack("<bhB", slave_id, speed, state)  # Slave ID, Speed (little-endian), and State

    # Calculate CRC for the full packet excluding the CRC itself
    packet_no_crc = dynamic_byte + start_byte + payload
    checksum = calc_crc(packet_no_crc)

    # Append CRC (little-endian)
    packet = packet_no_crc + struct.pack("<H", checksum)
    return packet

def send_packet(ser, slave_id: int, speed: int, state: int = STATE):
    """Send a hoverboard control packet."""
    packet = build_packet(slave_id, speed, state)
    ser.write(packet)
    ser.flush()

    # Debugging: Log the sent packet
    print(f"Sent packet to Slave {slave_id}: {packet.hex()}")

# ----------------------
# Main Communication Loop
# ----------------------
def demo_loop():
    # Setup the serial connection
    ser = serial.Serial(PORT, baudrate=BAUDRATE, timeout=1)
    print(f"Opened {PORT} @ {BAUDRATE} bps. Press Ctrl-C to stop.")

    try:
        while True:
            # Send constant speed to slave 0 (left motor)
            send_packet(ser, slave_id=0, speed=SPEED, state=STATE)

            # Send constant speed to slave 1 (right motor)
            send_packet(ser, slave_id=1, speed=SPEED, state=STATE)

            time.sleep(SEND_INTERVAL)  # Maintain consistent timing

    except KeyboardInterrupt:
        print("\nStopped by user.")
    finally:
        ser.close()
        print("Serial port closed.")

# ----------------------
# Entry Point
# ----------------------
if __name__ == "__main__":
    demo_loop()