from fastapi import APIRouter, HTTPException
from core import services

router = APIRouter()

@router.post("/lights_on")
async def lights_on():
    if services.lights:
        services.lights.headlights_on()
        return {"status": "lights_on"}
    else:
        raise HTTPException(status_code=503, detail="Lights unavailable")
    
@router.post("/lights_off")
async def lights_off():
    if services.lights:
        services.lights.headlights_off()
        return {"status": "lights_off"}
    else:
        raise HTTPException(status_code=503, detail="Lights unavailable")