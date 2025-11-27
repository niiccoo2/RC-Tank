#!/usr/bin/env python3
import struct
import serial  # type: ignore
import time

# ----------------------
# Config
# ----------------------
PORT = "/dev/serial0"  # Change this to your serial port (e.g., COMx on Windows)
BAUDRATE = 19200
SEND_INTERVAL = 0.1  # Delay between packets in seconds (100ms)

SPEED = 500  # Constant speed to be sent
STATE = 1  # Enabled

# Packet constants (based on documentation and INO code)
HEADER = b'\x0C\xFE'  # Header bytes from observed data
CMD_SET_SPEED = 0x01  # Command ID for setting speed and state

# ----------------------
# Serial Communication Helpers
# ----------------------
def open_serial(port=PORT, baud=BAUDRATE):
    """ Open a serial port with the specified configuration """
    ser = serial.Serial(port, baudrate=baud, timeout=0.1)
    ser.reset_input_buffer()
    ser.reset_output_buffer()
    return ser

def calc_crc(data: bytes) -> int:
    """ Calculate a simple CRC (Sum of bytes mod 65536) """
    return sum(data) & 0xFFFF

def build_packet(slave_id: int, speed: int, state: int = STATE) -> bytes:
    """
    Build a data packet for sending to the hoverboard.
    Packet structure:
    [HEADER(2)][CMD(1)][SLAVE_ID(1)][payload(6)][CRC(2)]
    Payload = speed(int16), state(uint16)
    """
    # Ensure speed and state are within valid bounds
    speed = max(-32768, min(32767, speed))
    state = state & 0xFFFF

    payload = struct.pack("<hH", speed, state)  # Little-endian: <hH -> int16, uint16
    crc_input = HEADER + bytes([CMD_SET_SPEED, slave_id]) + payload
    crc = calc_crc(crc_input)
    packet = crc_input + struct.pack("<H", crc)  # Append CRC (uint16)

    return packet

def send_packet(ser, slave_id: int, speed: int, state: int = STATE):
    """ Build and send a packet to the hoverboard via the serial port """
    packet = build_packet(slave_id, speed, state)
    ser.write(packet)
    ser.flush()
    print(f"Sent packet to Slave {slave_id}: Speed={speed}, State={state}")

# ----------------------
# Main Loop
# ----------------------
def demo_loop():
    ser = open_serial(PORT, BAUDRATE)
    print(f"Opened {PORT} @ {BAUDRATE} bps. Ctrl-C to stop.")
    
    try:
        while True:
            # Send constant speed (500) with state=1 to slave 0
            send_packet(ser, slave_id=0, speed=SPEED, state=STATE)

            # Send constant speed (500) with state=1 to slave 1
            send_packet(ser, slave_id=1, speed=SPEED, state=STATE)

            time.sleep(SEND_INTERVAL)  # Wait for the next cycle
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