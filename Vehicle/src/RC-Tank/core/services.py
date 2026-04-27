from drivers.motor import Motor
from drivers.lights import Lights
from drivers.gps import GPS
from drivers.webrtc import WebRTCManager
from drivers.compass import Compass

motors: Motor | None = None
webrtc: WebRTCManager | None = None
lights: Lights | None = None
gps: GPS | None = None
compass: Compass | None = None
