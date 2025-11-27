#!/usr/bin/env python3
import struct
import serial  # type: ignore
import time

# ----------------------
# Hoverboard Configuration
# ----------------------
PORT = "/dev/serial0"  # Serial connection to hoverboard
BAUDRATE = 19200  # Baud rate matches Arduino setup
SEND_INTERVAL = 0.05  # 50ms interval between transmissions
SPEED = 500  # Motor speed: -1000 to +1000
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
    Dynamic Byte + Start Byte + Slave ID + Speed + State + CRC
    """
    # Ensure valid ranges
    speed = max(-1000, min(1000, speed))  # Limit speed [-1000, 1000]
    state = state & 0xFF  # Limit state to a single byte

    # Dynamic Byte + Start Byte
    dynamic_byte = b'\xE3'  # Observed dynamic byte
    start_byte = b'\x2F'    # Start byte (`'/'` or 0x2F)

    # Payload: Slave ID (uint8), Speed (int16, little-endian), State (uint8)
    payload = struct.pack("<bhB", slave_id, speed, state)

    # Combine for CRC calculation
    packet_no_crc = dynamic_byte + start_byte + payload
    checksum = calc_crc(packet_no_crc)  # Generate CRC

    # Final packet: Add CRC at the end
    packet = packet_no_crc + struct.pack("<H", checksum)
    return packet

def send_packet(ser, slave_id: int, speed: int, state: int):
    """Send a hoverboard control packet."""
    packet = build_packet(slave_id, speed, state)
    ser.write(packet)
    ser.flush()

    # Debugging: Print each sent packet for verification
    print(f"Sent packet to Slave {slave_id}: {packet.hex()}")

# ----------------------
# Main Communication Loop
# ----------------------
def demo_loop():
    # Setup the serial connection
    ser = serial.Serial(PORT, baudrate=BAUDRATE, timeout=1)
    print(f"Opened serial port {PORT} @ {BAUDRATE} bps. Press Ctrl-C to stop.")

    try:
        while True:
            # Send to Slave 0 (left motor)
            send_packet(ser, slave_id=0, speed=SPEED, state=STATE)

            # Send to Slave 1 (right motor)
            send_packet(ser, slave_id=1, speed=SPEED, state=STATE)

            # Maintain 50ms interval
            time.sleep(SEND_INTERVAL)

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