from drivers.motor import Motor
from drivers.lights import Lights
from drivers.gps import GPS
from drivers.webrtc import WebRTCManager
from drivers.compass import Compass
from self_driving.self_driving import SelfDrivingManager

motors: Motor | None = None
webrtc: WebRTCManager | None = None
lights: Lights | None = None
gps: GPS | None = None
compass: Compass | None = None
self_driving_manager: SelfDrivingManager | None = None