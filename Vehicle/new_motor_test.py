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
CMD_BYTE = 0x82  # Command/Mode field
WSTATE_INITIAL = 0x01  # Initial state for wState
MAX_SPEED = 500  # Maximum speed amplitude for zigzag
PERIOD = 3  # Zigzag period in seconds

# ----------------------
# Globals
# ----------------------
w_state = WSTATE_INITIAL
next_state_time = time.time() + 3
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

def build_packet(slave_id: int, speed: int, state: int) -> bytes:
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
    state_byte = state.to_bytes(1, 'big')      # State field

    # Combine fields for CRC calculation
    packet_no_crc = start_byte + command_byte + struct.pack("<B", slave_id) + speed_bytes + state_byte
    checksum = calc_crc(packet_no_crc)  # Generate CRC for the packet

    # Final Packet: Prefix Start Byte and Append CRC
    packet = packet_no_crc + struct.pack("<H", checksum)
    return packet

def send_packet(slave_id: int, speed: int, state: int):
    """Send a hoverboard control packet."""
    global ser
    if ser is None:
        raise RuntimeError("Serial port is not open. Call demo_loop() or open the serial port before sending packets.")

    packet = build_packet(slave_id, speed, state)
    ser.write(packet)
    ser.flush()

    # Debugging: Print each sent packet
    print(f"Sent packet to Slave {slave_id} | Speed: {speed} | State: {state} | Packet: {packet.hex()}")

def calculate_speeds(t: float) -> tuple[int, int]:
    """Calculate dynamic speeds for zigzag behavior."""
    scaled_time = (t % PERIOD) / PERIOD  # Scaled time [0, 1)
    scale_factor = 1.6 * (min(max(PERIOD, 3), 9) / 9.0)  # Match Arduino scale factor

    # Calculate zigzag pattern speed
    iSpeed = int(
        scale_factor * MAX_SPEED * (
            abs(((scaled_time + 0.25) % 1) - 0.5) - 0.25
        ) * 4
    )
    iSteer = int(abs((scaled_time - 0.5) * 1600)) - 800

    # Calculate motor speeds
    iSpeedLeft = min(max(iSpeed + iSteer, -MAX_SPEED), MAX_SPEED)
    iSpeedRight = min(max(-iSpeed + iSteer, -MAX_SPEED), MAX_SPEED)

    return iSpeedLeft, iSpeedRight

def update_state():
    """Update state every 3 seconds."""
    global w_state, next_state_time

    if time.time() > next_state_time:
        next_state_time = time.time() + 3
        w_state <<= 1  # Cycle state by shifting left
        if w_state >= 64:
            w_state = 1  # Reset state to the initial state

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

            # Update motor state
            update_state()

            # Calculate motor speeds
            iSpeedLeft, iSpeedRight = calculate_speeds(current_time)

            # Send commands to motors
            send_packet(0, iSpeedLeft, w_state)  # Slave 0 (Left Motor)
            send_packet(1, iSpeedRight, w_state)  # Slave 1 (Right Motor)

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