from flask import Flask, request, jsonify, Response
import cv2
from flask_cors import CORS
import RPi.GPIO as GPIO  # type: ignore
import time
import atexit



app = Flask(__name__)
CORS(app)

LEFT_PWM_PIN = 13
RIGHT_PWM_PIN = 18

SERVO_FREQ_HZ = 50
ESC_MIN_DUTY = 4.5
ESC_NEUTRAL_DUTY = 7.5
ESC_MAX_DUTY = 10.5
ARM_TIME_SEC = 2.0

GPIO.setmode(GPIO.BCM)
GPIO.setup(LEFT_PWM_PIN, GPIO.OUT)
GPIO.setup(RIGHT_PWM_PIN, GPIO.OUT)

left = GPIO.PWM(LEFT_PWM_PIN, SERVO_FREQ_HZ)
right = GPIO.PWM(RIGHT_PWM_PIN, SERVO_FREQ_HZ)

# Init USB camera at 480p
usb_camera = cv2.VideoCapture(0)  # 0 = first USB cam
usb_camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)   # 480p width
usb_camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)  # 480p height
usb_camera.set(cv2.CAP_PROP_FPS, 30)
try:
    usb_camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)
except Exception:
    pass

def gen_frames():
    # Yields JPEG frames for MJPEG streaming
    while True:
        ok, frame = usb_camera.read()
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

def clamp(x, lo, hi):
    return max(lo, min(hi, x))

def throttle_to_duty(throttle: float) -> float:
    t = clamp(-throttle, -1.0, 1.0)
    if t >= 0:
        return ESC_NEUTRAL_DUTY + (ESC_MAX_DUTY - ESC_NEUTRAL_DUTY) * t
    else:
        return ESC_NEUTRAL_DUTY + (ESC_NEUTRAL_DUTY - ESC_MIN_DUTY) * t

def set_esc(pwm: GPIO.PWM, throttle: float):
    pwm.ChangeDutyCycle(throttle_to_duty(throttle))

def arm_escs():
    left.start(ESC_NEUTRAL_DUTY)
    right.start(ESC_NEUTRAL_DUTY)
    time.sleep(ARM_TIME_SEC)

def cleanup():
    set_esc(left, 0.0)
    set_esc(right, 0.0)
    time.sleep(0.3)
    left.stop()
    right.stop()
    GPIO.cleanup()

# Arm on startup
print("Arming ESCs...")
arm_escs()
print("Ready")

# Cleanup on exit
atexit.register(cleanup)

@app.route('/motor', methods=['POST'])
def set_motor():
    """
    POST /motor
    Body: {"left": -1.0 to 1.0, "right": -1.0 to 1.0}
    """
    print(f"Received motor command: {request.get_json()}")
    data = request.get_json()
    left_speed = float(data.get('left', 0.0))
    right_speed = float(data.get('right', 0.0))
    
    set_esc(left, left_speed)
    set_esc(right, right_speed)
    
    return jsonify({"status": "ok", "left": left_speed, "right": right_speed})

@app.route('/stop', methods=['POST'])
def stop():
    set_esc(left, 0.0)
    set_esc(right, 0.0)
    return jsonify({"status": "stopped"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)