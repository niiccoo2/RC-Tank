from core import services
from time import sleep
import threading
from core.config import get_logger
from self_driving.waypoint_navigation import WaypointNavigation
from core.states import self_driving_mode

self_driving = get_logger("self_driving")

class SelfDrivingManager:
  def __init__(self):
    self_driving_mode = 0
    self._thread = None
    self._running = False

    self.waypoint_navigation_object = WaypointNavigation()
  
  def start(self):
    if self._thread is None or not self._thread.is_alive():
      self._running = True
      self._thread = threading.Thread(target=self._run, daemon=True)
      self._thread.start()
      self_driving.debug("Self driving thread started")
  
  def stop(self):
    self_driving_mode = 0 # normal driving mode
    self._running = False
    if self._thread:
      self._thread.join(timeout=2)
      self_driving.debug("Self driving thread stopped")
      self._thread = None
  
  def _run(self):
    self_driving.debug("Self driving run loop running")
    while self._running:
      if services.motors is None:
        self_driving.warning("Self driving can't find motors")
        sleep(.1)
        continue
      
      # self_driving.debug(f"Self driving mode: {self.mode}")
      if self_driving_mode == 1:
        self.waypoint_navigation_object.waypoint_navigation()
      

      sleep(.1) # .5 seems to be too fast for the ESC's
    self_driving.debug("Exiting self-driving loop")
