from core.types import Location, GPSResponse

locations: list[Location] = []
gps_location: GPSResponse = GPSResponse(lat=0, lon=0, alt=0)
heading: float = 0