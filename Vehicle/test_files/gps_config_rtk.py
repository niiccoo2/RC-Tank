
import serial
import time
import os
import sys

# --- Configuration ---
SERIAL_PORT = "/dev/ttyACM0"

BAUD_RATES = [9600, 38400, 115200, 460800]
TARGET_BAUD = 38400

def get_checksum(message):
    """Calculates the 2-byte UBX checksum for a given message."""
    ck_a = 0
    ck_b = 0
    for char in message:
        ck_a = (ck_a + char) & 0xFF
        ck_b = (ck_b + ck_a) & 0xFF
    return bytes([ck_a, ck_b])

def send_ubx_msg(port, msg):
    """Constructs and sends a UBX message with a calculated checksum."""
    full_msg = bytes([0xB5, 0x62]) + msg
    full_msg += get_checksum(full_msg[2:])
    port.write(full_msg)
    time.sleep(0.1) # Give module time to process

def configure_for_rtk(port):
    """
    Configures a u-blox module for RTK operations.
    - Enables necessary raw measurement messages (RXM-RAWX, RXM-SFRBX).
    - Enables RTCM3 input on the primary UART/USB interface.
    - Sets a higher measurement rate.
    - Saves the configuration.
    """
    print(f"--- Configuring {port.name} for RTK ---")

    # CFG-MSG: Enable RXM-RAWX (Raw Measurements) - Class 0x02, ID 0x15
    send_ubx_msg(port, b'\x06\x01\x03\x00\x02\x15\x01')
    # CFG-MSG: Enable RXM-SFRBX (Subframe Data) - Class 0x02, ID 0x13
    send_ubx_msg(port, b'\x06\x01\x03\x00\x02\x13\x01')
    
    # CFG-MSG: Enable NAV-PVT (for local fix verification) - Class 0x01, ID 0x07
    send_ubx_msg(port, b'\x06\x01\x03\x00\x01\x07\x01')

    # CFG-PRT: Enable RTCM3 protocol input on the current port (e.g., UART1 or USB)
    # This assumes we are connected to the port we want to receive corrections on.
    # 0x01 = portID (UART1), can be 3 for USB. We configure both.
    # Port 1 (UART)
    send_ubx_msg(port, b'\x06\x00\x14\x00\x01\x00\x00\x00\xc0\x08\x00\x00' + TARGET_BAUD.to_bytes(4, 'little') + b'\x07\x00\x03\x00\x00\x00\x00\x00')
    # Port 3 (USB)
    send_ubx_msg(port, b'\x06\x00\x14\x00\x03\x00\x00\x00\xc0\x08\x00\x00' + TARGET_BAUD.to_bytes(4, 'little') + b'\x07\x00\x03\x00\x00\x00\x00\x00')

    # CFG-RATE: Set measurement rate to 4Hz (250ms)
    send_ubx_msg(port, b'\x06\x08\x06\x00\xfa\x00\x01\x00\x01\x00')

    # CFG-CFG: Save the current configuration to non-volatile memory (BBR and Flash)
    print("Saving configuration to module's non-volatile memory...")
    send_ubx_msg(port, b'\x06\x09\x0d\x00\x00\x00\x00\x00\xff\xff\x00\x00\x00\x00\x00\x00\x17')
    
    print("--- RTK Configuration Sent ---")
    time.sleep(0.5)

def verify_connection(port_name, baud_rate):
    """Tries to read a message from the GPS to verify communication."""
    try:
        with serial.Serial(port_name, baud_rate, timeout=2) as port:
            # A simple way to check for data is to read a few bytes
            port.read(10)
            # A more robust check involves trying to parse a message
            from ublox_gps import UbloxGps
            gps = UbloxGps(port)
            for _ in range(5):
                if gps.geo_coords():
                    return True
    except (serial.SerialException, ImportError):
        return False
    return False

def run():
    print("--- u-blox RTK Configuration Script ---")
    print(f"Target serial port: {SERIAL_PORT}")

    # 1. Find current baud rate
    current_baud = None
    print("Searching for current GPS baud rate...")
    for baud in BAUD_RATES:
        print(f"Testing {baud} bps...")
        if verify_connection(SERIAL_PORT, baud):
            print(f"Success! Found GPS at {baud} bps.")
            current_baud = baud
            break
    
    if not current_baud:
        print("\nError: Could not communicate with GPS module.")
        print("Check wiring, port name, and power. Ensure no other process is using the port.")
        return

    # 2. Configure the module
    try:
        with serial.Serial(SERIAL_PORT, current_baud, timeout=2) as port:
            # Set port to target baud rate first
            send_ubx_msg(port, b'\x06\x00\x14\x00\x01\x00\x00\x00\xc0\x08\x00\x00' + TARGET_BAUD.to_bytes(4, 'little') + b'\x01\x00\x01\x00\x00\x00\x00\x00')
            print(f"Switched module to {TARGET_BAUD} bps temporarily.")
            port.baudrate = TARGET_BAUD
            
            # Send the full RTK configuration
            configure_for_rtk(port)

        # 3. Verify configuration
        print("\n--- Verifying Configuration ---")
        if verify_connection(SERIAL_PORT, TARGET_BAUD):
            print(f"Successfully re-connected at {TARGET_BAUD} bps.")
            print("Configuration appears successful. The module is now ready for RTK.")
        else:
            print("Error: Failed to reconnect after configuration. Please power-cycle the GPS and re-run.")

    except serial.SerialException as e:
        print(f"Serial port error: {e}")
    except KeyboardInterrupt:
        print("\nScript stopped by user.")

if __name__ == '__main__':
    # This check is needed because the verification function imports ublox_gps
    try:
        from ublox_gps import UbloxGps
    except ImportError:
        print("Error: 'ublox_gps' library not found. Please install it using 'pip install ublox-gps'")
        sys.exit(1)
    run()
