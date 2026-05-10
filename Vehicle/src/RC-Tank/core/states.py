from core.types import WaypointLocation, Location
from typing import Any

waypoint_locations: list[Location] = []

gps_location: Location = Location(lat=0, lon=0, alt=0) 
"""alt should be in meters"""

ntrip_status: dict[str, Any] = {}

heading: float = 0