import RPi.GPIO as GPIO  # type: ignore
import time

# ESC signal pins (1 data pin per ESC). If you truly have only one output,
# set RIGHT_PWM_PIN = LEFT_PWM_PIN and wire both ESC signals to that pin.
LEFT_PWM_PIN = 18
RIGHT_PWM_PIN = 13  # set to 18 if sharing one pin

# Optional inversion per side
INVERT_LEFT = False
INVERT_RIGHT = False

# Servo/ESC timing
SERVO_FREQ_HZ = 50
ESC_MIN_DUTY = 5.0      # ~1.0 ms
ESC_NEUTRAL_DUTY = 7.5  # ~1.5 ms
ESC_MAX_DUTY = 10.0     # ~2.0 ms
ARM_TIME_SEC = 2.0

GPIO.setmode(GPIO.BCM)
GPIO.setup(LEFT_PWM_PIN, GPIO.OUT)
if RIGHT_PWM_PIN != LEFT_PWM_PIN:
    GPIO.setup(RIGHT_PWM_PIN, GPIO.OUT)

left = GPIO.PWM(LEFT_PWM_PIN, SERVO_FREQ_HZ)
right = left if RIGHT_PWM_PIN == LEFT_PWM_PIN else GPIO.PWM(RIGHT_PWM_PIN, SERVO_FREQ_HZ)

def clamp(x, lo, hi):
    return max(lo, min(hi, x))

def throttle_to_duty(throttle: float) -> float:
    t = clamp(throttle, -1.0, 1.0)
    if t >= 0:
        return ESC_NEUTRAL_DUTY + (ESC_MAX_DUTY - ESC_NEUTRAL_DUTY) * t
    else:
        return ESC_NEUTRAL_DUTY + (ESC_NEUTRAL_DUTY - ESC_MIN_DUTY) * t

def set_esc(pwm: GPIO.PWM, throttle: float, inverted: bool):
    t = -throttle if inverted else throttle
    pwm.ChangeDutyCycle(throttle_to_duty(t))

def arm_escs():
    left.start(ESC_NEUTRAL_DUTY)
    if right is not left:
        right.start(ESC_NEUTRAL_DUTY)
    time.sleep(ARM_TIME_SEC)

def neutral():
    set_esc(left, 0.0, INVERT_LEFT)
    set_esc(right, 0.0, INVERT_RIGHT)

print("Arming ESCs at neutral...")
arm_escs()
print("Ready. w=forward, s=reverse, x=neutral, q=quit")

try:
    while True:
        cmd = input("Input: ").strip().lower()
        if cmd == "w":
            set_esc(left, 0.3, INVERT_LEFT)
            set_esc(right, 0.3, INVERT_RIGHT)
        elif cmd == "s":
            # If reverse doesn't engage, some ESCs require brake-then-reverse.
            set_esc(left, -0.3, INVERT_LEFT)
            set_esc(right, -0.3, INVERT_RIGHT)
        elif cmd == "x":
            neutral()
        elif cmd == "q":
            break
        else:
            print("Use w/s/x/q")
finally:
    neutral()
    time.sleep(0.3)
    left.stop()
    if right is not left:
        right.stop()
    GPIO.cleanup()