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
from self_driving.self_driving import SelfDrivingManager
from core.config import get_logger
from time import time

lifecycle_logger = get_logger("lifecycle")

def initialize_components():
    global motors, webrtc, lights, gps

    lifecycle_logger.warning(f"Software started at {time()}")

    lifecycle_logger.warning("Initializing Motor...")
    try:
        services.motors = Motor()
        lifecycle_logger.warning("Motor initialized")
    except Exception as e:
        services.motors = None
        lifecycle_logger.warning(f"Motor init failed: {e}")
        traceback.print_exc()

    lifecycle_logger.warning("Initializing WebRTC...")
    try:
        services.webrtc = WebRTCManager()
        lifecycle_logger.warning("WebRTC initialized")
    except Exception as e:
        services.webrtc = None
        lifecycle_logger.warning(f"WebRTC init failed: {e}")
        traceback.print_exc()

    lifecycle_logger.warning("Initializing Lights...")
    try:
        services.lights = Lights()
        lifecycle_logger.warning("Lights initialized")
    except Exception as e:
        services.lights = None
        lifecycle_logger.warning(f"Lights init failed: {e}")
        traceback.print_exc()

    lifecycle_logger.warning("Initializing GPS...")
    try:
        services.gps = GPS()
        lifecycle_logger.warning("GPS initialized")
    except Exception as e:
        services.gps = None
        lifecycle_logger.warning(f"GPS init failed: {e}")
        traceback.print_exc()
    
    lifecycle_logger.warning("Initializing Compass...")
    try:
        services.compass = Compass()
        lifecycle_logger.warning("Compass initialized")
    except Exception as e:
        services.compass = None
        lifecycle_logger.warning(f"Compass init failed: {e}")
        traceback.print_exc()
    
    lifecycle_logger.warning("Initializing SelfDrivingManager...")
    try:
        services.self_driving_manager = SelfDrivingManager()
        lifecycle_logger.warning("SelfDrivingManager initialized")
    except Exception as e:
        services.self_driving_manager = None
        lifecycle_logger.warning(f"SelfDrivingManager init failed: {e}")
        traceback.print_exc()

@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_components()
    if services.lights: services.lights.side_on()
    if services.gps:
        threading.Thread(target=services.gps.update_gps_thread, daemon=True).start()
    if services.compass:
        threading.Thread(target=services.compass.update_compass_thread, daemon=True).start()
    if services.self_driving_manager: services.self_driving_manager.start()
    yield # shutdown
    if services.self_driving_manager: services.self_driving_manager.stop()
    if services.webrtc: await services.webrtc.cleanup()
    if services.motors: services.motors.cleanup()
    if services.lights: services.lights.off()