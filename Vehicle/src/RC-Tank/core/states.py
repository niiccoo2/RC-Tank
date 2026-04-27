from core.types import Location, GPSResponse

locations: list[Location] = []
gps_location: GPSResponse = GPSResponse(lat=0, lon=0, alt=0)
self_driving_mode: int = 0 # 0 = off, 1 = waypoints
heading: float = 0