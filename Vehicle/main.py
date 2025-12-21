from motor_class import Motor
from streamerClass import MJPEGStreamer

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from contextlib import asynccontextmanager
import asyncio
import time
import threading
import signal
import sys

# --------- Classes for HTTP Requests ----------
class MotorCommand(BaseModel):
    left: float
    right: float

# --------- Global Objects Initialization ----------
motors = Motor()

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

# --------- Lifespan Manager ---------
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up...")
    
    streamer.start()

    # Start the timeout check thread
    timeout_thread = threading.Thread(target=motors.timeout_check, daemon=True)
    timeout_thread.start()

    try:
        # Application is running
        yield
    finally:
        print("Shutting down...")
        streamer.stop()
        motors.cleanup()

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

    return {"status": "ok", "left": left_speed, "right": right_speed}

@app.post("/stop")
async def stop():
    """
    Stop both motors.
    """
    motors.set_esc(1, 0)
    motors.set_esc(0, 1)

    print("/stop ran")
    return {"status": "stopped"}

@app.post("/health")
async def health():
    print("/health ran")
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
    uvicorn.run(app, host='0.0.0.0', port=5000, timeout_graceful_shutdown=1)