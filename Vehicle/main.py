import RPi.GPIO as GPIO # type: ignore
import time

LEFT_MOTOR_PIN = 18
RIGHT_MOTOR_PIN = 13

GPIO.setmode(GPIO.BCM)
GPIO.setup(LEFT_MOTOR_PIN, GPIO.OUT)
GPIO.setup(RIGHT_MOTOR_PIN, GPIO.OUT)

# Standard RC ESC frequency
left = GPIO.PWM(LEFT_MOTOR_PIN, 50) # 50 Hz for RC ESC
right = GPIO.PWM(RIGHT_MOTOR_PIN, 50) # 50 Hz for RC ESC
left.start(0)
right.start(0)

print("Initializing ESC...")
left.ChangeDutyCycle(0)  # Minimum throttle (motor off)
right.ChangeDutyCycle(0)  # Minimum throttle (motor off)
time.sleep(2)  # Give ESC time to initialize

print("Running motor at ~10% throttle")
left.ChangeDutyCycle(6)  # Low speed
right.ChangeDutyCycle(6)  # Low speed
time.sleep(5)

print("Stopping motor")
left.ChangeDutyCycle(0)  # Back to min throttle
right.ChangeDutyCycle(0)  # Back to min throttle
