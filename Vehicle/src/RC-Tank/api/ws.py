import asyncio
from fastapi import APIRouter, WebSocket
from core.types import MotorCommand, RTCOffer, Location
from core import services, states
from api.telemetry import send_telemetry

router = APIRouter()

@router.websocket("/ws")
async def ws(ws: WebSocket):
    await ws.accept()
    telemetry_sender = asyncio.create_task(send_telemetry(ws))
    try:
        while True:
            msg = await ws.receive_json()
            msg_type = msg.get("type")

            print(f"{msg_type.upper()}: {msg['data']}")

            if len(msg_type.split(":")) > 1: # if has a prefix, in this case can only be two way
                msg_type = msg_type.split(":")[1] # now set type to the minor type. we can now treat all these messages as two way

                if msg_type == "ping":
                    await ws.send_json({"id": msg["id"], "type": "two_way_message:pong", "data": msg["data"]})
                elif msg_type == "webrtc_offer_request":
                    params = RTCOffer(**msg["data"])

                    if services.webrtc:
                        await ws.send_json({"id": msg["id"], "type": "two_way_message:webrtc_offer_response", "data": await services.webrtc.offer(params.model_dump())})
                    else:
                        pass # need to raise an error here

            else:
                msg_type = msg_type.split(":")[0]

                if msg_type == "motor":
                    cmd = MotorCommand(**msg["data"]) # ** makes it unpack a dict into a typed object

                    if services.motors:
                        services.motors.set_motor(cmd)
                    else:
                        pass # need to raise an error here
                elif msg_type == "lights":
                    if services.lights:
                        services.lights.set_headlights(msg["data"])
                    else:
                        pass # need to raise an error here
                elif msg_type == "waypoint_data":
                    locations_new_type: list[Location] = []
                    for item in msg["data"]:
                        locations_new_type.append(Location.from_waypoint(item))
                    states.waypoint_locations = locations_new_type
                    print(f"Recevied waypoint data: {locations_new_type}")
                elif msg_type == "self_driving_mode":
                    if services.self_driving_manager: services.self_driving_manager.set_mode(msg["data"])
                    print(f"Set self driving mode to: {msg['data']}")

    finally:
        if telemetry_sender: 
            telemetry_sender.cancel()