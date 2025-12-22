import RPi.GPIO as GPIO  # type: ignore
import time
import struct
import serial  # type: ignore
import time
import threading

BLACK = "\033[0;30m"
RED = "\033[0;31m"
GREEN = "\033[0;32m"
BROWN = "\033[0;33m"
BLUE = "\033[0;34m"
PURPLE = "\033[0;35m"
RESET = "\033[0m"

class Motor:
    def __init__(self,
                 port: str = "/dev/serial0",
                 baudrate: int = 4800,
                 send_interval: float = 0.1,
                 max_speed: int = 1000):
       
        self.PORT = port
        self.BAUDRATE = baudrate
        self.SEND_INTERVAL = send_interval # in s
        self.MAX_SPEED = max_speed

        self.ser = serial.Serial(self.PORT, baudrate=self.BAUDRATE, timeout=1)
        self.ser.reset_input_buffer()
        self.ser.reset_output_buffer()

        self.last_update_time = time.time()
        self._lock = threading.Lock()

        self.voltage: float = 0.0

        self.set_esc(0, 0) # Stop both motors
        self.set_esc(1, 0)
        self.stopped = True

        self._stop_event = threading.Event()
    
    def stop(self):
        """Request the timeout_check loop to exit."""
        self._stop_event.set()
    
    def calc_crc(self, data: bytes) -> int:
        crc = 0
        for byte in data:
            crc ^= (byte << 8)
            for _ in range(8):
                if crc & 0x8000:
                    crc = (crc << 1) ^ 0x1021
                else:
                    crc <<= 1
        return crc & 0xFFFF  # Ensure a 16-bit CRC

    def read_feedback(self):
        # Check if there is data in the buffer
        if self.ser.in_waiting > 0:
            # Read all available bytes
            data = self.ser.read(self.ser.in_waiting)
            # Process 'data' here (it will be bytes)
            print(f"Received: {data.hex()}")
            return data.hex()
        return

    def read_voltage_from_uart(self, data):
        """
        Read battery voltage from hoverboard UART data. 
        
        Args:
            data: bytes or bytearray from UART
            
        Returns: 
            float: Voltage in volts, or None if no valid packet found
        """
        # Convert to bytearray if needed
        if isinstance(data, str):
            # If hex string like "cdab01ae11f605..."
            data = bytes.fromhex(data. replace('\\x', ''))
        elif isinstance(data, bytes):
            data = bytearray(data)
        
        # Find start frame (CD AB)
        for i in range(len(data) - 14):  # Need at least 15 bytes
            if data[i] == 0xCD and data[i+1] == 0xAB:
                # Found start frame, extract voltage at bytes 5-6
                volt_lo = data[i + 5]
                volt_hi = data[i + 6]
                
                # Combine (little-endian)
                voltage_raw = (volt_hi << 8) | volt_lo
                
                # Convert to volts
                voltage = voltage_raw / 100.0
                
                return voltage
        
        return None  # No valid packet found
    
    def build_packet(self, iSlave: int, iSpeed: int, wState: int) -> bytes:
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
        checksum = self.calc_crc(payload_without_crc)  # Calculate checksum
        crc_bytes = struct.pack("<H", checksum)  # CRC (16-bit, little-endian)

        # Final packet: Append checksum
        return payload_without_crc + crc_bytes

    def send_packet(self, iSlave: int, iSpeed: int, wState: int):
        """Send the constructed hoverboard control packet."""
        if self.ser is None:
            raise RuntimeError("Serial port is not opened. Initialize it before sending packets.")

        packet = self.build_packet(iSlave, iSpeed, wState)
        
        with self._lock:
            self.ser.write(packet)
            # self.ser.flush() # Blocking, causes latency

        # Debugging: Show the sent packet
        # print(f"Sent packet | Slave: {iSlave} | Speed: {iSpeed} | State: {wState} | Packet: {packet.hex()}")

    def timeout_check(self):
        while not self._stop_event.is_set():
        # x 1000 to make it millis
            # print("Checking time")
            time_since_last_update = (time.time() - self.last_update_time)*1000
            # print(f"Time since last update: {time_since_last_update}")
            if time_since_last_update > 2000 and not self.stopped: # if over 2 sec
                print(f"{RED}TIMEOUT HIT ({time_since_last_update:.0f}ms), STOPPING{RESET}")
                self.set_esc(0, 0) # Stop both motors
                self.set_esc(1, 0)
                self.stopped = True
            
            self.read_feedback()

            self._stop_event.wait(0.1)
            # Need this to be responsive, but also not hog resources

    def clamp(self, x, lo, hi):
        return max(lo, min(hi, x))

    def set_esc(self, slave_id: int, throttle: int):
        self.send_packet(slave_id, throttle, 32)
        if throttle != 0.0:
            self.stopped = False
        voltage = self.read_voltage_from_uart(self.read_feedback())
        if voltage is not None:
            self.voltage = voltage

    def cleanup(self):
        self.set_esc(0, 0)
        self.set_esc(1, 0)
        time.sleep(0.3)
        self.ser.close()
