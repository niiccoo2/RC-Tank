#!/usr/bin/env python3
import struct
import serial  # type: ignore
import time

# ----------------------
# Hoverboard Configuration
# ----------------------
PORT = "/dev/serial0"  # Adjust as necessary for your system
BAUDRATE = 4800  # Matches Arduino setup
SEND_INTERVAL = 0.1  # 100ms interval between transmissions
MAX_SPEED = 1000  # Maximum speed for control
PERIOD = 6  # Zigzag period in seconds (increased to stay longer at speeds)
DEFAULT_STATE = 1  # Default state (e.g., Battery LED on)

# ----------------------
# Globals
# ----------------------
ser = None

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

def build_packet(iSlave: int, iSpeed: int, wState: int) -> bytes:
    """
    Build a hoverboard control packet:
    Start Byte (`0x2F`) + Slave + Speed + State + CRC
    """
    # Packet Data
    start_byte = b'\x2F'  # Start byte (`'/'`)
    slave_byte = struct.pack("<B", iSlave)  # Slave ID
    speed_bytes = struct.pack("<h", iSpeed)  # Speed (little-endian)
    state_byte = struct.pack("<B", wState)  # State

    # Combine fields for CRC calculation
    packet_no_crc = start_byte + slave_byte + speed_bytes + state_byte
    checksum = calc_crc(packet_no_crc)  # Generate CRC for the packet

    # Final Packet: Append CRC
    packet = packet_no_crc + struct.pack("<H", checksum)
    return packet

def send_packet(iSlave: int, iSpeed: int, wState: int):
    """Send a hoverboard control packet."""
    global ser
    if ser is None:
        raise RuntimeError("Serial port is not open. Call demo_loop() or open the serial port before sending packets.")

    packet = build_packet(iSlave, iSpeed, wState)
    ser.write(packet)
    ser.flush()

    # Debugging: Print each sent packet
    print(f"Sent packet | Slave: {iSlave} | Speed: {iSpeed} | State: {wState} | Packet: {packet.hex()}")

def calculate_speeds(t: float) -> int:
    """Calculate dynamic speed values."""
    SLOW_FACTOR = 10  # Slows down speed updates further

    adjusted_time = t / SLOW_FACTOR  # Adjust time to slow down transitions
    scaled_time = (adjusted_time % PERIOD) / PERIOD  # Scaled time [0, 1)

    # Zigzag pattern for speed calculation
    iSpeed = int(
        MAX_SPEED * (
            abs(((scaled_time + 0.25) % 1) - 0.5) * 2  # Oscillates between 0 and 1
        )
    )

    # Clamp values to valid ranges
    iSpeed = min(max(iSpeed, -MAX_SPEED), MAX_SPEED)

    return iSpeed

# ----------------------
# Main Communication Loop
# ----------------------
def demo_loop():
    global ser
    ser = serial.Serial(PORT, baudrate=BAUDRATE, timeout=1)
    print(f"Opened serial port {PORT} @ {BAUDRATE} bps. Press Ctrl-C to stop.")

    try:
        while True:
            current_time = time.time()

            # Calculate dynamic speed
            iSpeed = calculate_speeds(current_time)

            # Send control packets to two slaves
            send_packet(0, iSpeed, DEFAULT_STATE)  # Slave 0
            send_packet(1, -iSpeed, DEFAULT_STATE)  # Slave 1 (optional: reverse speed)

            # Maintain the send interval
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