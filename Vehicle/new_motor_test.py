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
MAX_STEER = 300  # Maximum steering value
PERIOD = 6  # Zigzag period in seconds (increased to stay longer at speeds)

# ----------------------
# Globals
# ----------------------
w_state_master = 0x20  # Default master state (32 = Battery LED indicator)
w_state_slave = 0x00  # Default slave state (0 = Off)
next_state_time = time.time() + 3  # Timing for cycling states
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

def build_packet(iSteer: int, iSpeed: int, wStateMaster: int, wStateSlave: int) -> bytes:
    """
    Build a hoverboard control packet:
    Start Byte (`0x2F`) + Steering + Speed + StateMaster + StateSlave + CRC
    """
    # Packet Data
    start_byte = b'\x2F'  # Start byte (`'/'`)
    steer_bytes = struct.pack("<h", iSteer)  # Steering (little-endian)
    speed_bytes = struct.pack("<h", iSpeed)  # Speed (little-endian)
    state_master_byte = wStateMaster.to_bytes(1, 'big')  # Master state
    state_slave_byte = wStateSlave.to_bytes(1, 'big')  # Slave state

    # Combine fields for CRC calculation
    packet_no_crc = start_byte + speed_bytes + steer_bytes + state_master_byte + state_slave_byte
    checksum = calc_crc(packet_no_crc)  # Generate CRC for the packet

    # Final Packet: Append CRC
    packet = packet_no_crc + struct.pack("<H", checksum)
    return packet

def send_packet(iSteer: int, iSpeed: int, wStateMaster: int, wStateSlave: int):
    """Send a hoverboard control packet."""
    global ser
    if ser is None:
        raise RuntimeError("Serial port is not open. Call demo_loop() or open the serial port before sending packets.")

    packet = build_packet(iSteer, iSpeed, wStateMaster, wStateSlave)
    ser.write(packet)
    ser.flush()

    # Debugging: Print each sent packet
    print(f"Sent packet | Steer: {iSteer} | Speed: {iSpeed} | StateMaster: {wStateMaster} | StateSlave: {wStateSlave} | Packet: {packet.hex()}")

def calculate_speeds_and_steer(t: float) -> tuple[int, int]:
    """Calculate dynamic speed and steer values."""
    SLOW_FACTOR = 2  # Slows down speed updates even further

    # Adjust PERID with a multiplier (SLOW_FACTOR elongates the switching time)
    adjusted_time = t / SLOW_FACTOR  
    scaled_time = (adjusted_time % PERIOD) / PERIOD  # Scaled time [0, 1)
    scale_factor = 1.6 * (min(max(PERIOD, 3), 9) / 9.0)  # Match Arduino scale factor

    # Calculate dynamic speed (zigzag pattern)
    iSpeed = int(
        scale_factor * MAX_SPEED * (
            abs(((scaled_time + 0.25) % 1) - 0.5) - 0.25
        ) * 4
    )
    # Calculate steering (oscillates between -MAX_STEER and +MAX_STEER)
    iSteer = int(abs((scaled_time - 0.5) * MAX_STEER * 2)) - MAX_STEER

    # Clamp values to valid ranges
    iSpeed = min(max(iSpeed, -MAX_SPEED), MAX_SPEED)
    iSteer = min(max(iSteer, -MAX_STEER), MAX_STEER)

    return iSteer, iSpeed

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
            # update_state()

            # Calculate dynamic speed and steering
            iSteer, iSpeed = calculate_speeds_and_steer(current_time)

            # Send a single control packet
            send_packet(0, iSpeed, w_state_master, w_state_slave)

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