from tankClass import Tank

from flask import Flask, request, jsonify, Response
import cv2 # pip install opencv-python
from flask_cors import CORS
import time
import atexit
import threading

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
usb_camera.set(cv2.CAP_PROP_FRAME_WIDTH, 160)
usb_camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 120)
usb_camera.set(cv2.CAP_PROP_FPS, 30)
try:
    usb_camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)
except Exception:
    pass

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
    tank.last_update_time = time.time()

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
    t = threading.Thread(target=tank.timeout_check, daemon=True)
    t.start()
    app.run(host='0.0.0.0', port=5000)