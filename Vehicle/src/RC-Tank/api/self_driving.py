from fastapi import APIRouter
from core.types import Location
from core import states

router = APIRouter()

@router.post("/save_waypoint_data")
async def save_waypoint_data(sent_locations: list[Location] = []):
    states.locations = sent_locations

@router.post("/start_self_driving")
async def start_self_driving():
   # do something with all the data to decide what to do here

   pass