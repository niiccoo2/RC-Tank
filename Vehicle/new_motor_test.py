#!/usr/bin/env python3
import struct
import serial  # type: ignore
import time

# ----------------------
# Hoverboard Configuration
# ----------------------
PORT = "/dev/serial0"  # Adjust depending on your hardware setup
BAUDRATE = 4800  # Matches default configuration in hoverboard firmware
SEND_INTERVAL = 0.1  # 100ms interval between transmissions
MAX_SPEED = 1000  # Maximum absolute motor speed
PERIOD = 6  # Zigzag period in seconds (speed changes every 3)

# ----------------------
# Globals
# ----------------------
ser = None  # Serial interface for communication

# ----------------------
# Utilities
# ----------------------
def calc_crc(data: bytes) -> int:
    crc = 0
    for byte in data:
        crc ^= (byte << 8)
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ 0x1021
            else:
                crc <<= 1
    return crc & 0xFFFF  # Ensure a 16-bit CRC

def build_packet(iSlave: int, iSpeed: int, wState: int) -> bytes:
    """
    Build UART packet in `SerialServer2Hover` format:
    Start Byte (1B) + Data Type (1B) + Slave ID (1B) + Speed (2B LE) + State (1B) + CRC (2B LE)
    """
    START_BYTE = b'\x2F'  # Start byte, `/` in ASCII
    DATA_TYPE = b'\x00'  # Data type (`0x00` for SerialServer2Hover)

    # Encode fields
    slave_byte = struct.pack("<B", iSlave)  # Slave ID, 1 byte
    speed_bytes = struct.pack("<h", iSpeed)  # Speed (signed 16-bit, little-endian)
    state_byte = struct.pack("<B", wState)  # State byte

    # Combine fields for CRC calculation
    payload_without_crc = START_BYTE + DATA_TYPE + slave_byte + speed_bytes + state_byte
    checksum = calc_crc(payload_without_crc)  # Calculate checksum
    crc_bytes = struct.pack("<H", checksum)  # CRC (16-bit, little-endian)

    # Final packet: Append checksum
    return payload_without_crc + crc_bytes

def send_packet(iSlave: int, iSpeed: int, wState: int):
    """Send the constructed hoverboard control packet."""
    global ser
    if ser is None:
        raise RuntimeError("Serial port is not opened. Initialize it before sending packets.")

    packet = build_packet(iSlave, iSpeed, wState)
    ser.write(packet)
    ser.flush()

    # Debugging: Show the sent packet
    print(f"Sent packet | Slave: {iSlave} | Speed: {iSpeed} | State: {wState} | Packet: {packet.hex()}")

def calculate_speeds(t: float) -> int:
    """Calculate a dynamic speed value based on time for a zigzag pattern."""
    scaled_time = (t % PERIOD) / PERIOD  # Scaled time [0, 1)
    speed = int(MAX_SPEED * abs(2 * ((scaled_time + 0.25) % 1) - 1))  # Zigzag pattern

    # Clamp speed to valid range
    return max(-MAX_SPEED, min(speed, MAX_SPEED))

# ----------------------
# Main Communication Loop
# ----------------------
def demo_loop():
    """Main loop for sending hoverboard control packets."""
    global ser
    ser = serial.Serial(PORT, baudrate=BAUDRATE, timeout=1)
    print(f"Opened serial port {PORT} at {BAUDRATE} bps. Press Ctrl-C to stop.")

    try:
        while True:
            current_time = time.time()

            # Calculate dynamic speed
            iSpeed = calculate_speeds(current_time)

            # Send control packets to both slaves
            send_packet(0, iSpeed, 32)  # Send to slave 0
            send_packet(1, -iSpeed, 32)  # Send to slave 1 (reverse speed for demonstration)

            # Wait before the next command
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