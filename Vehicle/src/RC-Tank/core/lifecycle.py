from contextlib import asynccontextmanager
import threading, traceback
from fastapi import FastAPI
from .services import motors, webrtc, lights, gps
from . import services
from drivers.motor import Motor
from drivers.lights import Lights
from drivers.gps import GPS
from drivers.webrtc import WebRTCManager
from drivers.compass import Compass

def initialize_components():
    global motors, webrtc, lights, gps

    print("Initializing Motor...")
    try:
        services.motors = Motor()
        print("Motor initialized")
    except Exception as e:
        services.motors = None
        print(f"Motor init failed: {e}")
        traceback.print_exc()

    print("Initializing WebRTC...")
    try:
        services.webrtc = WebRTCManager()
        print("WebRTC initialized")
    except Exception as e:
        services.webrtc = None
        print(f"WebRTC init failed: {e}")
        traceback.print_exc()

    print("Initializing Lights...")
    try:
        services.lights = Lights()
        print("Lights initialized")
    except Exception as e:
        services.lights = None
        print(f"Lights init failed: {e}")
        traceback.print_exc()

    print("Initializing GPS...")
    try:
        services.gps = GPS()
        print("GPS initialized")
    except Exception as e:
        services.gps = None
        print(f"GPS init failed: {e}")
        traceback.print_exc()
    
    print("Initializing Compass...")
    try:
        services.compass = Compass()
        print("Compass initialized")
    except Exception as e:
        services.compass = None
        print(f"Compass init failed: {e}")
        traceback.print_exc()

@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_components()
    if services.lights: services.lights.side_on()
    if services.motors:
        threading.Thread(target=services.motors.timeout_check, daemon=True).start()
    if services.gps:
        threading.Thread(target=services.gps.update_gps_thread, daemon=True).start()
    if services.compass:
        threading.Thread(target=services.compass.update_compass_thread, daemon=True).start()
    yield
    if services.webrtc: await services.webrtc.cleanup()
    if services.motors: services.motors.cleanup()
    if services.lights: services.lights.off()