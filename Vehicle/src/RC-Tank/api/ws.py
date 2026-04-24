from fastapi import APIRouter, WebSocket
from api import lights
from core.types import MotorCommand
from core.services import motors

router = APIRouter()

@router.websocket("/ws")
async def ws(ws: WebSocket):
    await ws.accept()
    while True:
        msg = await ws.receive_json()
        msg_type = msg.get("type")

        print(f"{msg_type.upper()}: {msg['data']}")

        if msg_type == "motor":
            cmd = MotorCommand(**msg["data"]) # ** makes it unpack a dict into a typed object

            if motors is not None:
                motors.set_motor(cmd)
            else:
                pass # need to raise ann error here
        elif msg_type == "lights":
            lights.set_headlights
        elif msg_type == "config":
            # handle_config(msg["data"])
            pass