from core import services, states
from core.types import MotorCommand, Location
from time import sleep
import math
from core.config import get_logger
import time

import os
from dotenv import load_dotenv

self_driving = get_logger("self_driving")

class WaypointNavigation:
  def __init__(self):
    pass

  def waypoint_navigation(self, max_speed: int = 500, success_distance: float = 2):
    """
    Navigate through a list of waypoints.
    
    Args:
    max_speed: int that defines speed to be changed to turn
    success_distance: float that defines how close you need to be in meters to a waypoint to switch to next one
    """
    if len(states.waypoint_locations) == 0: # if no waypoints, stop code
      self.mode = 0
    
    last_time = time.time()
    error = 0
    integral = 0
    derivative = 0
    control = 0
    previous_error = 0

    # KP = 1
    # KI = 0
    # KD = 0
    TURNING_CONSTANT = 8

    for waypoint in states.waypoint_locations:
      last_time = time.time()

      # when more than x meters away form waypoint, keep trying to drive to it
      while self._calc_distance(waypoint, states.gps_location) > success_distance:
        if self.mode != 1:
          self_driving.debug("Shouldn't be in self driving mode! Stopping.")
          if services.motors:
            services.motors.set_motor(MotorCommand(left=1234_0000, right=1234_0000)) #1234_0000 = stop and make sure it is stopped
          return
        
        load_dotenv()
        KP = float(os.getenv("KP", "0"))
        KI = float(os.getenv("KI", "0"))
        KD = float(os.getenv("KD", "0"))

        # self_driving.debug(f"Going to waypoint {waypoint}")
        bearing_to_waypoint = self._calc_bearing_to_waypoint(states.gps_location, waypoint)
        heading = states.heading

        difference = bearing_to_waypoint - heading

        if difference > 180: # make sure we are using the shortest path
          difference -= 360
        elif difference < -180:
          difference += 360

        normalized_difference = difference/360

        # self_driving.debug(f"Difference: {normalized_difference}")

        # PID STUFF

        # error = setpoint - pv
        # integral += error * dt
        # derivative = (error - previous_error) / dt
        # control = kp * error + ki * integral + kd * derivative

        current_time = time.time()
        dt = current_time - last_time

        if dt <= 0:
            dt = 0.001

        error = difference
        integral += error * dt
        integral = max(min(integral, 100), -100) # clamp
        derivative = (error - previous_error) / dt
        control = KP * error + KI * integral + KD * derivative

        last_time = current_time
        previous_error = error

        left_speed = max_speed-(TURNING_CONSTANT*(-control))
        right_speed = max_speed-(TURNING_CONSTANT*(control))

        ###########

        self_driving.debug(f"{bearing_to_waypoint}, {heading}")

        # TURNING_CONSTANT = 800

        # left_speed = max_speed-(TURNING_CONSTANT*(-normalized_difference))
        # right_speed = max_speed-(TURNING_CONSTANT*(normalized_difference))

        # self_driving.debug(f"Self driving speeds: {left_speed}, {right_speed}")

        if services.motors:
          services.motors.set_motor(MotorCommand(left=left_speed, right=right_speed))
        else:
          self_driving.debug("Was unable to set motor speed")
        sleep(.01)
  
  def _calc_bearing_to_waypoint(self, current: Location, waypoint: Location):
    lat1 = math.radians(current.lat)
    lat2 = math.radians(waypoint.lat)
    dlon = math.radians(waypoint.lon - current.lon)
    dlat = math.radians(waypoint.lat - current.lat)

    # scale lon by cos(mean_lat) to make a local tangent-plane
    x = dlon * math.cos((lat1 + lat2) / 2.0)
    y = dlat

    bearing = (math.degrees(math.atan2(x, y)) + 360) % 360
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