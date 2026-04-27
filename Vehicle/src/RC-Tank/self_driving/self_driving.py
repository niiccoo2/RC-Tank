from core import services, states
from core.types import MotorCommand, Location, GPSResponse
from time import sleep
import threading
import math

class SelfDrivingManager:
  MODE_OFF = 0
  MODE_WAYPOINT = 1

  def __init__(self):
    self.mode = SelfDrivingManager.MODE_OFF
    self._thread = None
    self._running = False
  
  def start(self):
    if self._thread is None or not self._thread.is_alive():
      self._running = True
      self._thread = threading.Thread(target=self._run, daemon=True)
      self._thread.start()
      print("Self driving thread started")
  
  def stop(self):
    self._running = False
    if self._thread:
      self._thread.join(timeout=2)
      print("Self driving thread stopped")
      self._thread = None
  
  def set_mode(self, mode):
    print(f"Switching mode to {mode}")
    self.mode = mode
  
  def _run(self):
    print("Self driving run loop running")
    while self._running:
      if services.motors is None:
        print("Self driving can't find motors")
        sleep(.1)
        continue

      if self.mode == SelfDrivingManager.MODE_WAYPOINT:
        self._waypoint_navigation()
      else:
        services.motors.set_motor(MotorCommand(left=0, right=0))
      sleep(.05)
    print("Exiting self-driving loop")
  
  def _waypoint_navigation(self):
    for waypoint in states.locations:
      bearing_to_waypoint = self._calc_bearing_to_waypoint(states.gps_location, waypoint)
      

  def _calc_bearing_to_waypoint(self, current: GPSResponse, waypoint: Location):
    x_diff = waypoint.latLng[0] - current.lat
    y_diff = waypoint.latLng[1] - current.lon

    bearing = math.degrees(math.atan2(y_diff, x_diff))

    if bearing < 0:
      bearing = 360+bearing
    
    return bearing