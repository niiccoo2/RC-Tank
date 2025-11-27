#!/usr/bin/env python3
import struct
import serial  # type: ignore
import time

# ----------------------
# Hoverboard Configuration
# ----------------------
PORT = "/dev/serial0"  # Adjust as necessary for your system
BAUDRATE = 19200  # Matches Arduino setup
SEND_INTERVAL = 0.05  # 50ms interval between transmissions
SPEED = 500  # Motor speed: -1000 to +1000
CMD_BYTE = 0x82  # Command/Mode field observed in Arduino structure
STATE = 0xFF  # State: Enabled or all bits set

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

def build_packet(slave_id: int, speed: int) -> bytes:
    """
    Build a hoverboard packet matching Arduino examples:
    Start Byte (`0x2F`) + Command Byte + Speed + State + CRC
    """
    # Ensure valid ranges
    speed = max(-1000, min(1000, speed))  # Limit speed [-1000, 1000]

    # Packet Data
    start_byte = b'\x2F'             # Start byte (`'/'`)
    command_byte = CMD_BYTE.to_bytes(1, 'big')  # `0x82`
    speed_bytes = struct.pack("<h", speed)     # Motor speed (little-endian)
    state_byte = STATE.to_bytes(1, 'big')      # State field (`0xFF`)

    # Combine fields for CRC calculation
    packet_no_crc = start_byte + command_byte + struct.pack("<B", slave_id) + speed_bytes + state_byte
    checksum = calc_crc(packet_no_crc)  # Generate CRC for the packet

    # Final Packet: Prefix Start Byte and Append CRC
    packet = packet_no_crc + struct.pack("<H", checksum)
    return packet

def send_packet(ser, slave_id: int, speed: int):
    """Send a hoverboard control packet."""
    packet = build_packet(slave_id, speed)
    ser.write(packet)
    ser.flush()

    # Debugging: Print each sent packet
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
            send_packet(ser, slave_id=0, speed=SPEED)

            # Send to Slave 1 (right motor)
            send_packet(ser, slave_id=1, speed=SPEED)

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