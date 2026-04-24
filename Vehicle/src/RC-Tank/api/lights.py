from core import services

def set_headlights(level: int):
    if services.lights:
        services.lights.headlights(level)
        return {"status": "ok", "level": f"{level}"}
    else:
        return "Lights unavailable"