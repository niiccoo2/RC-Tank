#!/usr/bin/env python3
import struct
import serial  # type: ignore
import time

# ----------------------
# Configuration
# ----------------------
PORT = "/dev/serial0"  # Adjust as necessary ("/dev/ttyS0" or "COMx" for Windows)
BAUDRATE = 19200  # Matches Arduino code and hoverboard expectations
SEND_INTERVAL = 0.05  # 50ms (matches `SEND_MILLIS` in Arduino)
SPEED = 500  # Constant speed for motors (-1000 to 1000)
STATE = 1  # Enabled state as described in Arduino examples

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
    return crc & 0xFFFF  # Ensure CRC remains 16-bit

def build_packet(slave_id: int, speed: int, state: int = STATE) -> bytes:
    """
    Build a hoverboard data packet similar to Arduino.
    Packet structure:
    [START (1)][SLAVE_ID (1)][SPEED (2)][STATE (1)][CRC (2)]
    """
    # Ensure values fit expected ranges
    speed = max(-1000, min(1000, speed))  # Clamp speed to [-1000, 1000]
    state = state & 0xFF  # Ensure state is an 8-bit value

    # Start byte and other fields before the CRC
    start_byte = b'\x2F'  # Start marker '/' (0x2F or defined `'/`' char)
    payload = struct.pack("<bhB", slave_id, speed, state)  # Signed Speed (int16), and state (uint8)

    # Combine everything except the CRC for checksum calculation
    packet_no_crc = start_byte + payload
    checksum = calc_crc(packet_no_crc)  # Generate the checksum

    # Attach the CRC (little-endian format)
    packet = packet_no_crc + struct.pack("<H", checksum)
    return packet

def send_packet(ser, slave_id: int, speed: int, state: int = STATE):
    """Build and send a hoverboard command packet over serial."""
    packet = build_packet(slave_id, speed, state)
    ser.write(packet)
    ser.flush()

    # Debugging: Log sent data
    print(f"Sent packet to Slave {slave_id}: {packet.hex()}")

# ----------------------
# Main Communication Loop
# ----------------------
def demo_loop():
    # Initialize serial communication
    ser = serial.Serial(PORT, baudrate=BAUDRATE, timeout=1)
    print(f"Opened {PORT} @ {BAUDRATE} bps. Press Ctrl-C to stop.")

    try:
        while True:
            # Send a constant speed command to both slave IDs (left and right motors)
            send_packet(ser, slave_id=0, speed=SPEED, state=STATE)  # Left motor
            send_packet(ser, slave_id=1, speed=SPEED, state=STATE)  # Right motor

            time.sleep(SEND_INTERVAL)  # Maintain consistent timing between packets

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