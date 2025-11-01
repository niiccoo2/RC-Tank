from flask import Flask, request, jsonify, Response
import cv2 # pip install opencv-python
from flask_cors import CORS
import RPi.GPIO as GPIO  # type: ignore
import time
import atexit
import asyncio

# Colors
BLACK = "\033[0;30m"
RED = "\033[0;31m"
GREEN = "\033[0;32m"
BROWN = "\033[0;33m"
BLUE = "\033[0;34m"
PURPLE = "\033[0;35m"
RESET = "\033[0m"

app = Flask(__name__)
CORS(app)

# LEFT_PWM_PIN = 13
# RIGHT_PWM_PIN = 18

# SERVO_FREQ_HZ = 50
# ESC_MIN_DUTY = 4.5
# ESC_NEUTRAL_DUTY = 7.5
# ESC_MAX_DUTY = 10.5
# ARM_TIME_SEC = 2.0

# Init USB camera at 480p
usb_camera = cv2.VideoCapture(0)  # 0 = first USB cam
usb_camera.set(cv2.CAP_PROP_FRAME_WIDTH, 150)
usb_camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 120)
usb_camera.set(cv2.CAP_PROP_FPS, 30)
try:
    usb_camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)
except Exception:
    pass

class Tank:
    
    def __init__(self,
                 left_pwm_pin: int = 13,
                 right_pwm_pin: int = 18,
                 servo_freq_hz: int = 50,
                 esc_min_duty: float = 4.5,
                 esc_neutral_duty: float = 7.5,
                 esc_max_duty: float = 10.5,
                 arm_time_sec: float = 2.0):
        self.LEFT_PWM_PIN = left_pwm_pin
        self.RIGHT_PWM_PIN = right_pwm_pin
        self.SERVO_FREQ_HZ = servo_freq_hz
        self.ESC_MIN_DUTY = esc_min_duty
        self.ESC_NEUTRAL_DUTY = esc_neutral_duty
        self.ESC_MAX_DUTY = esc_max_duty
        self.ARM_TIME_SEC = arm_time_sec

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.LEFT_PWM_PIN, GPIO.OUT)
        GPIO.setup(self.RIGHT_PWM_PIN, GPIO.OUT)

        self.left = GPIO.PWM(self.LEFT_PWM_PIN, self.SERVO_FREQ_HZ)
        self.right = GPIO.PWM(self.RIGHT_PWM_PIN, self.SERVO_FREQ_HZ)

        self.last_update_time = time.time()

        self.set_esc(self.left, 0.0) # Stop both motors
        self.set_esc(self.right, 0.0)
        self.stopped = True

    async def timeout_check(self):
        while True:
        # x 1000 to make it millis
            print("Checking time")
            time_since_last_update = (time.time() - self.last_update_time)*1000
            print(f"Time since last update: {time_since_last_update}")
            if time_since_last_update > 1000 and not self.stopped: # if over 1 sec
                self.set_esc(self.left, 0.0) # Stop both motors
                self.set_esc(self.right, 0.0)
                self.stopped = True
            time.sleep(0.100)
            # Need this to be responsive, but also not hog resources

    def clamp(self, x, lo, hi):
        return max(lo, min(hi, x))

    def throttle_to_duty(self, throttle: float) -> float:
        t = self.clamp(-throttle, -1.0, 1.0)
        print(f"{PURPLE}Setting throttle to: {throttle}, Clamped: {t}{RESET}")
        if t >= 0:
            return self.ESC_NEUTRAL_DUTY + (self.ESC_MAX_DUTY - self.ESC_NEUTRAL_DUTY) * t
        else:
            return self.ESC_NEUTRAL_DUTY + (self.ESC_NEUTRAL_DUTY - self.ESC_MIN_DUTY) * t

    def set_esc(self, pwm: GPIO.PWM, throttle: float):
        pwm.ChangeDutyCycle(self.throttle_to_duty(throttle))
        if throttle != 0.0:
            self.stopped = False

    def arm_escs(self):
        self.left.start(self.ESC_NEUTRAL_DUTY)
        self.right.start(self.ESC_NEUTRAL_DUTY)
        time.sleep(self.ARM_TIME_SEC)

    def cleanup(self):
        self.set_esc(self.left, 0.0)
        self.set_esc(self.right, 0.0)
        time.sleep(0.3)
        self.left.stop()
        self.right.stop()
        GPIO.cleanup()

tank = Tank()

def gen_frames():
    # Yields JPEG frames for MJPEG streaming
    while True:
        ok, frame = usb_camera.read()
        frame = cv2.rotate(frame, cv2.ROTATE_180)
        if not ok:
            time.sleep(0.05)
            continue
        ok, buf = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 70])  # adjust quality to save data
        if not ok:
            continue
        jpg = buf.tobytes()
        yield (b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n'
            b'Content-Length: ' + str(len(jpg)).encode() + b'\r\n\r\n' +
            jpg + b'\r\n')

@app.route('/camera')
def camera():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/motor', methods=['POST'])
def set_motor():
    """
    POST /motor
    Body: {"left": -1.0 to 1.0, "right": -1.0 to 1.0}
    """
    global last_update_time
    last_update_time = time.time()

    data = request.get_json()
    print(f"Received motor command: {data}")
    left_speed = float(data.get('left', 0.0))
    right_speed = float(data.get('right', 0.0))
    
    tank.set_esc(tank.left, left_speed)
    tank.set_esc(tank.right, right_speed)
    
    return jsonify({"status": "ok", "left": left_speed, "right": right_speed})

@app.route('/stop', methods=['POST'])
def stop():
    tank.set_esc(tank.left, 0.0)
    tank.set_esc(tank.right, 0.0)
    return jsonify({"status": "stopped"})

# Arm on startup
print("Arming ESCs...")
tank.arm_escs()
print("Ready")

# Cleanup on exit
atexit.register(tank.cleanup)

if __name__ == '__main__':
    asyncio.run(tank.timeout_check())
    app.run(host='0.0.0.0', port=5000)