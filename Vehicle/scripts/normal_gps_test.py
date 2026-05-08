from serial import Serial
from pygnssutils import GNSSNTRIPClient, GNSSReader
from queue import Queue, Empty
import os
from dotenv import load_dotenv

load_dotenv()

SER_PORT = "/dev/ttyACM0"
SER_BAUD = 38400

NTRIP_SERVER = "macorsrtk.massdot.state.ma.us"
NTRIP_PORT = 10000
NTRIP_MOUNT = "RTCM3MSM_IMAX"

# Use fixed reference coords (good for testing caster disconnects).
# Replace with your actual approximate location if you want.
REFLAT = 42.370152
REFLON = -71.172057
REFALT = 0.0
REFSEP = 0.0

stream = Serial(SER_PORT, SER_BAUD, timeout=1)
gnr = GNSSReader(stream)
out_queue = Queue()

def describe_ntrip_item(raw, parsed) -> str:
    """
    Create a readable one-line description of whatever came from the NTRIP client.
    """
    ident = getattr(parsed, "identity", type(parsed).__name__)
    raw_len = len(raw) if isinstance(raw, (bytes, bytearray, memoryview)) else -1
    return f"NTRIP: {ident} ({raw_len} bytes)"

with GNSSNTRIPClient(None) as gnc:
    gnc.run(
        server=NTRIP_SERVER,
        port=NTRIP_PORT,
        mountpoint=NTRIP_MOUNT,
        datatype="RTCM",
        ntripuser=os.getenv("NTRIP_USER"),
        ntrippassword=os.getenv("NTRIP_PWD"),
        ggainterval=10,   # 10s is typical; 2s can annoy some casters
        ggamode=1,        # fixed reference coords (prevents many caster disconnects)
        reflat=REFLAT,
        reflon=REFLON,
        refalt=REFALT,
        refsep=REFSEP,
        output=out_queue,
    )

    while True:
        # 1) Drain NTRIP queue quickly; print what arrives; inject RTCM raw bytes into receiver
        try:
            while True:
                raw, parsed = out_queue.get_nowait()

                # Print what we got from caster
                print(describe_ntrip_item(raw, parsed))

                # Inject only the raw bytes into the GNSS receiver
                if isinstance(raw, (bytes, bytearray, memoryview)) and raw:
                    stream.write(bytes(raw))

                out_queue.task_done()
        except Empty:
            pass

        # 2) Read GNSS receiver output and show NAV-PVT RTK status
        raw_gnss, parsed_gnss = gnr.read()
        if parsed_gnss is not None and getattr(parsed_gnss, "identity", None) == "NAV-PVT":
            rtk_status = {0: "None", 1: "Float", 2: "Fixed"}.get(parsed_gnss.carrSoln, "Unknown")
            print(
                f"Fix: {parsed_gnss.fixType}D | RTK: {rtk_status} | "
                f"NTRIP Age: {parsed_gnss.lastCorrectionAge}s | "
                f"Sats: {parsed_gnss.numSV} | "
                f"Lat: {parsed_gnss.lat}, Lon: {parsed_gnss.lon}"
            )