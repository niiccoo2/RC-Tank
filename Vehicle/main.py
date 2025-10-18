import RPi.GPIO as GPIO
import time

ESC_PIN = 18  # Replace with your correct PWM pin

GPIO.setmode(GPIO.BCM)
GPIO.setup(ESC_PIN, GPIO.OUT)

# Standard RC ESC frequency
pwm = GPIO.PWM(ESC_PIN, 50)  # 50 Hz for RC ESC
pwm.start(0)

try:
    print("Initializing ESC...")
    pwm.ChangeDutyCycle(5)  # Minimum throttle (motor off)
    time.sleep(2)  # Give ESC time to initialize

    print("Running motor at ~10% throttle")
    pwm.ChangeDutyCycle(6)  # Low speed
    time.sleep(5)

    print("Stopping motor")
    pwm.ChangeDutyCycle(5)  # Back to min throttle

finally:
    pwm.stop()
    GPIO.cleanup()
