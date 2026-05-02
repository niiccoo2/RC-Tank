from core import services, states
from core.types import MotorCommand, WaypointLocation, Location
from time import sleep
import threading
import math

class SelfDrivingManager:
  def __init__(self):
    self.mode = 0
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
  
  def set_mode(self, mode: int):
    print(f"Switching mode to {mode}")
    self.mode = mode
  
  def _run(self):
    print("Self driving run loop running")
    last_mode = 0
    while self._running:
      if services.motors is None:
        print("Self driving can't find motors")
        sleep(.1)
        continue
      
      # print(f"Self driving mode: {self.mode}")
      if self.mode == 1:
        self._waypoint_navigation()
      elif last_mode != 0:
        services.motors.set_motor(MotorCommand(left=12340000, right=12340000))

      last_mode = self.mode
      sleep(.1) # .5 seems to be too fast for the ESC's
    print("Exiting self-driving loop")
  
  def _waypoint_navigation(self, max_speed: int = 500, success_distance: float = 1):
    """
    Navigate through a list of waypoints.
    
    Args:
    max_speed: int that defines speed to be changed to turn
    success_distance: float that defines how close you need to be to a waypoint to switch to next one
    """
    if len(states.waypoint_locations) == 0: # if no waypoints, stop code
      self.mode = 0
    for waypoint in states.waypoint_locations:
      # when more than 2 meters away form waypoint, keep trying to drive to it
      while self._calc_distance(waypoint, states.gps_location) > 2:
        if self.mode != 1:
          print("Shouldn't be in self driving mode! Stopping.")
          return

        print(f"Going to waypoint {waypoint}")
        bearing_to_waypoint = self._calc_bearing_to_waypoint(states.gps_location, waypoint)
        heading = states.heading

        difference = bearing_to_waypoint - heading

        if difference > 180: # make sure we are using the shortest path
          difference -= 360
        elif difference < -180:
          difference += 360

        normalized_difference = difference/360

        print(f"Difference: {normalized_difference}")

        TURNING_CONSTANT = 1500

        left_speed = max_speed-(TURNING_CONSTANT*(-normalized_difference))
        right_speed = max_speed-(TURNING_CONSTANT*(normalized_difference))

        print(f"Self driving speeds: {left_speed}, {right_speed}")

        if services.motors:
          services.motors.set_motor(MotorCommand(left=left_speed, right=right_speed))
        else:
          print("Was unable to set motor speed")


  def _calc_bearing_to_waypoint(self, current: Location, waypoint: Location):
    """
    Calculate bearing from one position to another.
    """
    # might want to change this to use the correct math, but I don't really understand how the correct math works...

    x_diff = waypoint.lat - current.lat
    y_diff = waypoint.lon - current.lon

    bearing = math.degrees(math.atan2(y_diff, x_diff))

    if bearing < 0:
      bearing += 360
    elif bearing > 360:
      bearing -= 360
    
    return bearing
  
  def _calc_distance(self, location_1: Location, location_2: Location):
    """
    Calculate distance from two locations in meters.
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(math.radians, [location_1.lon, location_1.lat, location_2.lon, location_2.lat])

    difference_lon = lon2 - lon1
    difference_lat = lat2 - lat1
    a = math.sin(difference_lat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(difference_lon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    r = 6_378_137 # radius of earth in m

    distance = c * r
    return distance