from flask import Flask, request, jsonify
from flask_cors import CORS
import RPi.GPIO as GPIO  # type: ignore
import time
import atexit

app = Flask(__name__)
CORS(app)

LEFT_PWM_PIN = 13
RIGHT_PWM_PIN = 18

SERVO_FREQ_HZ = 50
ESC_MIN_DUTY = 4.1
ESC_NEUTRAL_DUTY = 7.5
ESC_MAX_DUTY = 10.9
ARM_TIME_SEC = 2.0

GPIO.setmode(GPIO.BCM)
GPIO.setup(LEFT_PWM_PIN, GPIO.OUT)
GPIO.setup(RIGHT_PWM_PIN, GPIO.OUT)

left = GPIO.PWM(LEFT_PWM_PIN, SERVO_FREQ_HZ)
right = GPIO.PWM(RIGHT_PWM_PIN, SERVO_FREQ_HZ)

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