from core import services, states
from fastapi import WebSocket, WebSocketException
import asyncio

async def send_telemetry(ws: WebSocket, websocket_logger):
  websocket_logger.debug("Starting telemetry")
  if services.gps is None:
    websocket_logger.error("GPS unavailable")
    raise WebSocketException(1011, "GPS unavailable")
  if services.motors is None:
    websocket_logger.error("Motors unavailable")
    raise WebSocketException(1011, "Motors unavailable")
  while True:
    gps_data = states.gps_location
    
    if hasattr(gps_data, "model_dump"):
      gps_value = gps_data.model_dump()
    elif hasattr(gps_data, "dict"):
      gps_value = gps_data.dict()
    else:
      gps_value = gps_data

    data = {
      "type": "telemetry", 
      "data": {
        "gps": gps_value,
        "heading": states.heading,
        "voltage": services.motors.voltage
      }
    }

    await ws.send_json(data)
    websocket_logger.debug(f"Sending telemetry: {data}")

    await asyncio.sleep(1)