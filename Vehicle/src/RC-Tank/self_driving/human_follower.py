from core.states import self_driving_mode
from core import services
from core.types import MotorCommand
from core.config import get_logger

self_driving = get_logger("self_driving")

class HumanFollower:
  def __init__(self):
    pass

  def follow_human(self):
    while True: # for each frame? not really sure how this will work
      if self_driving_mode != 2:
        self_driving.debug("Shouldn't be in self driving mode! Stopping.")
        if services.motors:
          services.motors.set_motor(MotorCommand(left=1234_0000, right=1234_0000)) #1234_0000 = stop and make sure it is stopped
        return