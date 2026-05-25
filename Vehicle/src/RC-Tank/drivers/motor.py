import time
import struct
import serial  # type: ignore
import threading
from core.types import MotorCommand
from core.config import get_logger

motor = get_logger("motor")

BLACK = "\033[0;30m"
RED = "\033[0;31m"
GREEN = "\033[0;32m"
BROWN = "\033[0;33m"
BLUE = "\033[0;34m"
PURPLE = "\033[0;35m"
RESET = "\033[0m"

class Motor:
    def __init__(self,
                 port: str = "/dev/ttyTHS1",
                 baudrate: int = 19200,
                 send_interval: float = 0.1,
                 max_speed: int = 1000):
       
        self.PORT = port
        self.BAUDRATE = baudrate
        self.SEND_INTERVAL = send_interval # in s
        self.MAX_SPEED = max_speed

        self.ser = serial.Serial(self.PORT, baudrate=self.BAUDRATE, timeout=1)
        self.ser.reset_input_buffer()
        self.ser.reset_output_buffer()

        self._state_lock = threading.Lock()
        self.last_update_time = time.time()
        self.desired_left = 0
        self.desired_right = 0
        self.applied_left = 0
        self.applied_right = 0

        self.voltage: float = 0.0

        self.stopped = True

        self._stop_event = threading.Event()
        self._io_thread = threading.Thread(target=self._io_worker, daemon=True)
        self._io_thread.start()
    
    def stop(self):
        """Request the I/O loop to exit and wait for shutdown."""
        self._stop_event.set()
        if self._io_thread.is_alive():
            self._io_thread.join(timeout=2)
    
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
        try:
            waiting = self.ser.in_waiting
            if waiting > 0:
                data = self.ser.read(waiting)
                if data:
                    motor.debug(f"Received: {data.hex()}")
                    return data
        except serial.SerialException as exc:
            motor.error(f"{RED}Serial read failed: {exc}{RESET}")
            raise
        return None

    def read_voltage_from_uart(self, data):
        """
        Read battery voltage from hoverboard UART data.  
        
        Args: 
            data: bytes or bytearray from UART
            
        Returns:  
            float: Voltage in volts, or None if no valid packet found
        """
        # Handle None or empty data
        if data is None or len(data) == 0:
            return None
        
        # Convert to bytearray if needed
        if isinstance(data, str):
            # If hex string like "cdab01ae11f605..."
            data = bytes.fromhex(data. replace('\\x', ''))
        elif isinstance(data, bytes):
            data = bytearray(data)
        
        # Need at least 15 bytes for a complete packet
        if len(data) < 15:
            return None
        
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
        self.ser.write(packet)
        # self.ser.flush() # Blocking, causes latency

        # Debugging: Show the sent packet
        # motor.debug(f"Sent packet | Slave: {iSlave} | Speed: {iSpeed} | State: {wState} | Packet: {packet.hex()}")

    def _send_pair(self, left_speed: int, right_speed: int) -> bool:
        try:
            self.set_esc(0, left_speed)  # slave 0 is left
            self.set_esc(1, right_speed)  # slave 1 is right
            return True
        except serial.SerialException as exc:
            motor.error(f"{RED}Serial write failed: {exc}{RESET}")
            return False

    def _set_safe_stopped_state(self):
        with self._state_lock:
            self.desired_left = 0
            self.desired_right = 0
            self.applied_left = 0
            self.applied_right = 0
            self.stopped = True

    def _io_worker(self):
        while not self._stop_event.is_set():
            now = time.time()
            with self._state_lock:
                desired_left = self.desired_left
                desired_right = self.desired_right
                time_since_last_update = (now - self.last_update_time) * 1000

            timeout_hit = time_since_last_update > 2000
            if timeout_hit:
                if not self.stopped:
                    motor.error(f"{RED}TIMEOUT HIT ({time_since_last_update:.0f}ms), STOPPING{RESET}")
                sent = self._send_pair(0, 0)
                if sent:
                    self._send_pair(0, 0)  # Do this twice because of a weird bug with ESC
                    with self._state_lock:
                        self.applied_left = 0
                        self.applied_right = 0
                        self.stopped = True
                else:
                    self._set_safe_stopped_state()
            else:
                sent = self._send_pair(desired_left, desired_right)
                if sent:
                    with self._state_lock:
                        self.applied_left = desired_left
                        self.applied_right = desired_right
                        self.stopped = (desired_left == 0 and desired_right == 0)
                else:
                    self._set_safe_stopped_state()

            try:
                feedback = self.read_feedback()
                if feedback:
                    voltage = self.read_voltage_from_uart(feedback)
                    if voltage is not None:
                        self.voltage = voltage
                    else:
                        motor.debug("Warning: Could not parse voltage from feedback")
            except serial.SerialException:
                self._set_safe_stopped_state()
                self._stop_event.wait(self.SEND_INTERVAL)

            self._stop_event.wait(self.SEND_INTERVAL)

        self._send_pair(0, 0)
        self._send_pair(0, 0)
        self._set_safe_stopped_state()

    def clamp(self, x, lo, hi):
        return max(lo, min(hi, x))

    def set_esc(self, slave_id: int, throttle: int):
        self.send_packet(slave_id, throttle, 32)
        if throttle != 0:
            self.stopped = False
    
    def set_motor(self, command: MotorCommand):
        """
        Set the speed of the tank's motors.
        Takes left and right speeds, -1000 to 1000.
        Example:
        {
            "left": 500,
            "right": -500
        }
        """

        if command.left == 1234_0000 or command.right == 1234_0000:
            command.left = 0
            command.right = 0

        command.left = self.clamp(command.left, -1000, 1000)
        command.right = self.clamp(command.right, -1000, 1000)

        left_speed = int(-command.left)
        right_speed = int(command.right)

        with self._state_lock:
            self.last_update_time = time.time()
            self.desired_left = left_speed
            self.desired_right = right_speed
            applied_left = self.applied_left
            applied_right = self.applied_right
            voltage = self.voltage

        motor.debug(f'motor ran, left: {left_speed}, right: {right_speed}')

        return {"status": "ok", "left": applied_left, "right": applied_right, 'voltage': voltage}

    def cleanup(self):
        self.stop()
        if self.ser and self.ser.is_open:
            self.ser.close()
