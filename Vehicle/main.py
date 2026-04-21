from motor_class import Motor
from peripherals import Lights
from gps_class import GPS, GPSResponse
from webrtc_manager import WebRTCManager

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from contextlib import asynccontextmanager
import time
import threading
import signal
import sys
import traceback
import asyncio

# --------- Classes for HTTP Requests ----------
class MotorCommand(BaseModel):
    left: float
    right: float

class RTCOffer(BaseModel):
    sdp: str
    type: str

class Location(BaseModel):
    ID: int
    latLng: list[float]
# --------- Global Objects Initialization ----------
motors = None
webrtc = None
lights = None
gps = None


def initialize_components():
    global motors, webrtc, lights, gps

    print("Initializing Motor...")
    try:
        motors = Motor()
        print("Motor initialized")
    except Exception as e:
        motors = None
        print(f"Motor init failed: {e}")
        traceback.print_exc()

    print("Initializing WebRTC...")
    try:
        webrtc = WebRTCManager()
        print("WebRTC initialized")
    except Exception as e:
        webrtc = None
        print(f"WebRTC init failed: {e}")
        traceback.print_exc()

    print("Initializing Lights...")
    try:
        lights = Lights()
        print("Lights initialized")
    except Exception as e:
        lights = None
        print(f"Lights init failed: {e}")
        traceback.print_exc()

    print("Initializing GPS...")
    try:
        gps = GPS()
        print("GPS initialized")
    except Exception as e:
        gps = None
        print(f"GPS init failed: {e}")
        traceback.print_exc()

# --------- Lifespan Manager ---------
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up...")
    initialize_components()

    if lights is not None:
        lights.side_on()
    else:
        print("Skipping lights startup: Lights unavailable")

    # Start the timeout check thread
    if motors is not None:
        timeout_thread = threading.Thread(target=motors.timeout_check, daemon=True)
        timeout_thread.start()
    else:
        print("Skipping motor timeout thread: Motor unavailable")

    try:
        # Application is running
        yield
    finally:
        # This runs when the program is stopped
        print("Shutting down...")
        if webrtc is not None:
            await webrtc.cleanup()
        if motors is not None:
            motors.cleanup()
        if lights is not None:
            lights.off()

# --------- FastAPI Application ---------
app = FastAPI(lifespan=lifespan)

# Enable CORS middleware for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this with your allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------- ROUTES ----------
@app.get("/gps")
async def get_gps():
    if gps is None:
        raise HTTPException(status_code=503, detail="GPS unavailable")
    try:
        response = await asyncio.to_thread(gps.read_data)
        return response
    except Exception as e:
        print(f"GPS read failed: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="GPS read failed") from e

@app.post("/offer")
async def offer(params: RTCOffer):
    """
    WebRTC Signaling Endpoint.
    Takes an SDP offer, configures the connection, and returns an SDP answer.
    """
    
    if webrtc is None:
        raise HTTPException(status_code=503, detail="WebRTC unavailable")

    return await webrtc.offer(params.model_dump())

@app.post("/motor")
async def set_motor(command: MotorCommand):
    """
    Set the speed of the tank's motors.
    POST body takes left and right speeds, -1.0 to 1.0.
    Example:
    {
        "left": 0.5,
        "right": -0.5
    }
    """
    if motors is None:
        raise HTTPException(status_code=503, detail="Motor unavailable")

    motors.last_update_time = time.time()

    left_speed = int(-command.left)
    right_speed = int(command.right)

    motors.set_esc(0, left_speed) # slave 0 is left
    motors.set_esc(1, right_speed) # slave 1 is right

    print(f'/motor ran, left: {left_speed}, right: {right_speed}')

    return {"status": "ok", "left": left_speed, "right": right_speed, 'voltage': motors.voltage}

@app.post("/stop")
async def stop():
    """
    Stop both motors.
    """
    if motors is None:
        raise HTTPException(status_code=503, detail="Motor unavailable")

    motors.set_esc(1, 0)
    motors.set_esc(0, 1)

    print("/stop ran")
    return {"status": "stopped"}

@app.post("/lights_off")
async def lights_off():
    if lights:
        lights.headlights_off()
        return {"status": "lights_off"}
    else:
        raise HTTPException(status_code=503, detail="Lights unavailable")

@app.post("/lights_on")
async def lights_on():
    if lights:
        lights.headlights_on()
        return {"status": "lights_on"}
    else:
        raise HTTPException(status_code=503, detail="Lights unavailable")

@app.head("/health")
async def health():
    return {
        "status": "healthy",
        "components": {
            "motor": motors is not None,
            "lights": lights is not None,
            "gps": gps is not None,
            "webrtc": webrtc is not None,
        },
    }

@app.post("/start_self_driving")
async def start_self_driving(locations: list[Location] = []):
    print(f"Got a call to start self driving!")
    print(locations)

def signal_handler(sig, frame):
    print("\nShutting down gracefully...")
    if motors is not None:
        motors.cleanup()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# Run the FastAPI app
if __name__ == '__main__':
    import uvicorn
    uvicorn.run(
        app, 
        host='0.0.0.0', 
        port=5000, 
        timeout_graceful_shutdown=1,
        ssl_keyfile="./key.pem", 
        ssl_certfile="./cert.pem"
    )