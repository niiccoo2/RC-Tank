from core.types import WaypointLocation, Location

waypoint_locations: list[Location] = []
gps_location: Location = Location(lat=0, lon=0, alt=0)
heading: float = 0