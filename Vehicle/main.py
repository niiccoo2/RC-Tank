from motor_class import Motor
from peripherals import Lights, Fan
from gps_class import GPS, GPSResponse
from streamer_class import MJPEGStreamer
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

# --------- Classes for HTTP Requests ----------
class MotorCommand(BaseModel):
    left: float
    right: float

class RTCOffer(BaseModel):
    sdp: str
    type: str

# --------- Global Objects Initialization ----------
motors = Motor()

# MJPEG Streamer (Legacy/Backup)
streamer = MJPEGStreamer(
    src=0,
    width=320,              # Slightly higher resolution
    height=240,
    cam_fps=30,
    fourcc_str="MJPG",
    rotate_180=True,
    jpeg_quality=35,        # Lower quality = smaller frames = faster transmission
    motion_gate=False,      # Disable motion gating to reduce latency
    share_encoded=True
)

# WebRTC Manager (New)
# Note: src=0 might conflict if both MJPEG and WebRTC try to open it.
# You should probably only use one at a time or use a different source.
# For now, we initialize it but it only opens camera when requested.
webrtc = WebRTCManager(cam_src="0") 

fan = Fan()
lights = Lights()
gps = GPS()

# --------- Lifespan Manager ---------
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up...")

    if not fan.on():
        print("Warning: Fan control failed - check permissions")
    
    streamer.start()

    lights.side_on()

    # Start the timeout check thread
    timeout_thread = threading.Thread(target=motors.timeout_check, daemon=True)
    timeout_thread.start()

    try:
        # Application is running
        yield
    finally:
        # This runs when the program is stopped
        print("Shutting down...")
        streamer.stop()
        await webrtc.cleanup()
        motors.cleanup()
        lights.off()
        fan.off()

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
    response = gps.read_data()

    return response

@app.get("/camera")
async def camera(fps: int = 24, q: int | None = None):
    """
    Stream the MJPEG camera feed.
    Optional query params:
      - fps: Frames per second (default: 12, range: 1-30)
      - q: JPEG quality (only used if share_encoded=False)
    """
    fps = max(1, min(30, fps))  # Clamp FPS between 1 and 30
    return StreamingResponse(
        streamer.gen_frames(max_fps=fps, quality_override=q),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )

@app.post("/offer")
async def offer(params: RTCOffer):
    """
    WebRTC Signaling Endpoint.
    Takes an SDP offer, configures the connection, and returns an SDP answer.
    """
    # If using WebRTC, we might want to stop MJPEG to free the camera
    streamer.stop() 
    
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
    motors.set_esc(1, 0)
    motors.set_esc(0, 1)

    print("/stop ran")
    return {"status": "stopped"}

@app.post("/lights_off")
async def lights_off():
    if lights:
        lights.headlights_off()
    else:
        print('Lights object not defined')

@app.post("/lights_on")
async def lights_on():
    if lights:
        lights.headlights_on()
    else:
        print('Lights object not defined')

@app.post("/health")
async def health():
    return {"status": "healthy"}

def signal_handler(sig, frame):
    print("\nShutting down gracefully...")
    if streamer is not None:
        streamer.stop()
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