from fastapi import APIRouter, HTTPException
from core import services
from core.types import MotorCommand
import time

router = APIRouter()

@router.post("/motor")
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
    if services.motors is None:
        raise HTTPException(status_code=503, detail="Motor unavailable")

    services.motors.last_update_time = time.time()

    left_speed = int(-command.left)
    right_speed = int(command.right)

    services.motors.set_esc(0, left_speed) # slave 0 is left
    services.motors.set_esc(1, right_speed) # slave 1 is right

    print(f'/motor ran, left: {left_speed}, right: {right_speed}')

    return {"status": "ok", "left": left_speed, "right": right_speed, 'voltage': services.motors.voltage}

@router.post("/stop")
async def stop():
    """
    Stop both motors.
    """
    if services.motors is None:
        raise HTTPException(status_code=503, detail="Motor unavailable")

    services.motors.set_esc(1, 0)
    services.motors.set_esc(0, 0)

    print("/stop ran")
    return {"status": "stopped"}