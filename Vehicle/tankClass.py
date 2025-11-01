import RPi.GPIO as GPIO  # type: ignore
import time

BLACK = "\033[0;30m"
RED = "\033[0;31m"
GREEN = "\033[0;32m"
BROWN = "\033[0;33m"
BLUE = "\033[0;34m"
PURPLE = "\033[0;35m"
RESET = "\033[0m"

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

    def timeout_check(self):
        while True:
        # x 1000 to make it millis
            print("Checking time")
            time_since_last_update = (time.time() - self.last_update_time)*1000
            print(f"Time since last update: {time_since_last_update}")
            if time_since_last_update > 1000 and not self.stopped: # if over 1 sec
                print(f"{RED}TIMEOUT HIT, STOPPING{RESET}")
                self.set_esc(self.left, 0.0) # Stop both motors
                self.set_esc(self.right, 0.0)
                self.stopped = True
            time.sleep(0.5)
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