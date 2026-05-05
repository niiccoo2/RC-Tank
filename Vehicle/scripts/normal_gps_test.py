from serial import Serial
from pygnssutils import GNSSNTRIPClient, GNSSReader
from queue import Queue
import os
from dotenv import load_dotenv

load_dotenv()

# 1. Connect to your GPS hardware
stream = Serial('/dev/ttyACM0', 38400, timeout=3)
out_queue = Queue()

# 2. Start the NTRIP Client (Caster Info)
with GNSSNTRIPClient(None) as gnc:
    gnc.run(
        server="macorsrtk.massdot.state.ma.us", 
        port=10000, 
        mountpoint="RTCM3MSM_IMAX", 
        output=out_queue,  # Corrections go into this queue
        ntripuser=os.getenv("NTRIP_USER"),
        ntrippass=os.getenv("NTRIP_PWD")
    )

    # 3. Simple Loop: Send corrections to GPS & Read "Good" result
    while True:
        if not out_queue.empty():
            stream.write(out_queue.get()) # Inject RTCM into GPS

        gnr = GNSSReader(stream)
        (raw, parsed) = gnr.read()
        if parsed is not None:
            if parsed.identity == "NAV-PVT":
                print(f"Fix type {parsed.fixType}: {parsed.lat}, {parsed.lon}")
