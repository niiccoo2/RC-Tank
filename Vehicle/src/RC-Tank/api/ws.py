from fastapi import APIRouter, WebSocket
from api import motor
from core.types import MotorCommand

router = APIRouter()

@router.websocket("/ws")
async def ws(ws: WebSocket):
    await ws.accept()
    while True:
        msg = await ws.receive_json()
        msg_type = msg.get("type")

        print(f"Got request: {msg_type}")

        if msg_type == "motor":
            cmd = MotorCommand(**msg["data"]) # ** makes it unpack a dict into a typed object
            motor.set_motor(cmd)
        elif msg_type == "ping":
            # await ws.send_json({"type":"pong"})
            pass
        elif msg_type == "config":
            # handle_config(msg["data"])
            pass