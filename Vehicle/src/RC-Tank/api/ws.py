from fastapi import APIRouter, WebSocket

router = APIRouter()

@router.websocket("/ws")
async def ws(ws: WebSocket):
    await ws.accept()
    while True:
        msg = await ws.receive_json()
        msg_type = msg.get("type")

        print(f"Got request: {msg_type}")

        if msg_type == "control":
            # handle_control(msg["data"])
            pass
        elif msg_type == "ping":
            # await ws.send_json({"type":"pong"})
            pass
        elif msg_type == "config":
            # handle_config(msg["data"])
            pass