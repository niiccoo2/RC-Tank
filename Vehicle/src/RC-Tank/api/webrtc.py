from fastapi import APIRouter, HTTPException
from core import services
from core.types import RTCOffer

router = APIRouter()

@router.post("/offer")
async def offer(params: RTCOffer):
    """
    WebRTC Signaling Endpoint.
    Takes an SDP offer, configures the connection, and returns an SDP answer.
    """
    
    if services.webrtc is None:
        raise HTTPException(status_code=503, detail="WebRTC unavailable")

    return await services.webrtc.offer(params.model_dump())