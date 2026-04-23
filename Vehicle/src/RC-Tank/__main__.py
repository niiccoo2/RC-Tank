from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

from core.lifecycle import lifespan
from api import gps, health, lights, motor, self_driving, webrtc

BASE_DIR = Path(__file__).resolve().parent.parent  # adjust as needed
ssl_keyfile = BASE_DIR / "config" / "key.pem"
ssl_certfile = BASE_DIR / "config" / "cert.pem"

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# register routes
app.include_router(gps.router)
app.include_router(health.router)
app.include_router(lights.router)
app.include_router(motor.router)
app.include_router(self_driving.router)
app.include_router(webrtc.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=5000,
        timeout_graceful_shutdown=1,
        ssl_keyfile=ssl_keyfile,
        ssl_certfile=ssl_certfile
    )