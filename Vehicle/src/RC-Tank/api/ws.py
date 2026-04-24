from fastapi import APIRouter, WebSocket
from core.types import MotorCommand, RTCOffer
from core import services

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

            if services.motors:
                services.motors.set_motor(cmd) # this returns data such as voltage that we need to somehow send to client
            else:
                pass # need to raise an error here
        elif msg_type == "lights":
            if services.lights:
                services.lights.set_headlights(msg["data"])
            else:
                pass # need to raise an error here
        elif msg_type == "ping":
            await ws.send_json({"type": "pong", "data": {msg["data"]}})
        elif msg_type == "webrtc":
            params = RTCOffer(**msg["data"])

            if services.webrtc:
                await ws.send_json(services.webrtc.offer(params.model_dump()))
            else:
                pass # need to raise an error here