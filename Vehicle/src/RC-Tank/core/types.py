from pydantic import BaseModel

class Location(BaseModel):
    ID: int
    latLng: list[float]

class RTCOffer(BaseModel):
    sdp: str
    type: str

class MotorCommand(BaseModel):
    left: float
    right: float

class GPSResponse(BaseModel):
    lat: float
    lon: float
    alt: float