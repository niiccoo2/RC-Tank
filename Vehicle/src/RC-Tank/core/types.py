from pydantic import BaseModel

class WaypointLocation(BaseModel):
    ID: int
    latLng: list[float]

class RTCOffer(BaseModel):
    sdp: str
    type: str

class MotorCommand(BaseModel):
    left: float
    right: float

class Location(BaseModel):
    lat: float
    lon: float
    alt: float

    @classmethod
    def from_waypoint(cls, data: WaypointLocation):
        result: Location = Location(lat = 0, lon = 0, alt = 0)
        if isinstance(data, dict):
            latLng = data['latLng']
        else:
            latLng = data.latLng

        result.lat = latLng[0]
        result.lon = latLng[1]

        return cls(
            lat = result.lat,
            lon = result.lon,
            alt = 0.0
        )