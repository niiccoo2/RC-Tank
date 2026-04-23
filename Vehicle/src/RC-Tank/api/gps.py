from fastapi import APIRouter, HTTPException
from core import services
import traceback
import asyncio

router = APIRouter()

@router.get("/gps")
async def get_gps():
    if services.gps is None:
        raise HTTPException(status_code=503, detail="GPS unavailable")
    try:
        response = await asyncio.to_thread(services.gps.read_data)
        return response
    except Exception as e:
        print(f"GPS read failed: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="GPS read failed") from e