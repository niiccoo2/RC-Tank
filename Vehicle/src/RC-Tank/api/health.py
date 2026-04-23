from fastapi import APIRouter
from core import services

router = APIRouter()

@router.head("/health")
async def health():
    return {
        "status": "healthy",
        "components": {
            "motor": services.motors is not None,
            "lights": services.lights is not None,
            "gps": services.gps is not None,
            "webrtc": services.webrtc is not None,
        },
    }