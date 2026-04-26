from core.states import self_driving_mode, locations
from core import services
from core.types import MotorCommand
from time import sleep

def self_driving():
  if services.motors:
    while True:
      if self_driving_mode != 0: # if ANY form of self driving mode is on
        # this looks redundant but once we have more modes it will help
        if self_driving_mode == 1:
          waypoint_navigation()
        
        services.motors.set_motor(MotorCommand(left = 0, right = 0))
      sleep(.05)

def waypoint_navigation():
  while self_driving_mode == 1:
    # will calc what heading and how to direct motors

    sleep(.05)
