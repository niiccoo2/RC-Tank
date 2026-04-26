from core import services
from fastapi import WebSocket, WebSocketException
import traceback
import asyncio

async def send_telemetry(ws: WebSocket):
  if services.gps is None:
    raise WebSocketException(1011, "GPS unavailable")
  if services.motors is None:
    raise WebSocketException(1011, "Motors unavailable")
  while True:
    gps_data = await asyncio.to_thread(services.gps.read_data)
    data = {
      "type": "telemetry", 
      "data": {
        "gps": gps_data,
        "voltage": services.motors.voltage
      }
    }

    await ws.send_json(data)
    print(f"Sending telemetry: {data}")

    await asyncio.sleep(1)