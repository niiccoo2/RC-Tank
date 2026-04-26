from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from core.lifecycle import lifespan
from api import ws

BASE_DIR = Path(__file__).resolve().parents[2]
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

app.include_router(ws.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=5000,
        timeout_graceful_shutdown=1,
        ssl_keyfile=str(ssl_keyfile),
        ssl_certfile=str(ssl_certfile)
    )