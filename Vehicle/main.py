from motor_class import Motor

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from contextlib import asynccontextmanager
import time
import threading
import signal
import sys

from fastrtc import Stream, VideoStreamHandler
import cv2
import numpy as np

# --------- Classes for HTTP Requests ----------
class MotorCommand(BaseModel):
    left: float
    right: float

# --------- FastAPI Application ---------
app = FastAPI()

motors = Motor()

# Enable CORS middleware for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this with your allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------- Tank and Camera Initialization ----------
# tank = Tank()

# Camera configuration
CAM_SRC = 0
CAM_WIDTH = 320
CAM_HEIGHT = 240
CAM_FPS = 30
ROTATE_180 = True

# Initialize camera capture
cap = cv2.VideoCapture(CAM_SRC)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAM_WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAM_HEIGHT)
cap.set(cv2.CAP_PROP_FPS, CAM_FPS)
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
try:
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
except Exception:
    pass


def video_handler(frame: np.ndarray) -> np.ndarray:
    """
    Process video frames for WebRTC streaming.
    Captures from camera, rotates 180 degrees if configured,
    and converts BGR to RGB for proper color display.
    
    Note: The `frame` parameter is required by FastRTC's VideoStreamHandler
    interface but is not used since we're in 'send' mode (server sends video
    to client, not receiving from client).
    """
    _ = frame  # Unused - required by FastRTC interface for send mode
    ret, camera_frame = cap.read()
    if not ret:
        # Return a black frame if camera read fails
        return np.zeros((CAM_HEIGHT, CAM_WIDTH, 3), dtype=np.uint8)

    # Rotate 180 degrees if configured
    if ROTATE_180:
        camera_frame = cv2.rotate(camera_frame, cv2.ROTATE_180)

    # Convert BGR to RGB for proper color display
    rgb_frame = cv2.cvtColor(camera_frame, cv2.COLOR_BGR2RGB)

    return rgb_frame


# Create WebRTC stream with VideoStreamHandler
stream = Stream(
    handler=VideoStreamHandler(video_handler, fps=CAM_FPS),
    modality="video",
    mode="send",
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up...")

    # Start the timeout check thread
    timeout_thread = threading.Thread(target=motors.timeout_check, daemon=True)
    timeout_thread.start()

    try:
        # Application is running
        yield
    finally:
        print("Shutting down...")
        cap.release()
        motors.cleanup()

# Assign lifespan handler to FastAPI app
app.router.lifespan_context = lifespan

# Mount WebRTC stream endpoints to FastAPI app
stream.mount(app)

# --------- ROUTES ----------

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

    motors.set_esc(1, left_speed) # slave 1 is left
    motors.set_esc(0, right_speed) # slave 0 is right

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
    if cap is not None:
        cap.release()
    if motors is not None:
        motors.cleanup()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# Run the FastAPI app
if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=5000, timeout_graceful_shutdown=1)