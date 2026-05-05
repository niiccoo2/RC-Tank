from serial import Serial
from pygnssutils import GNSSNTRIPClient, GNSSReader
from queue import Queue, Empty
import os
from dotenv import load_dotenv

load_dotenv()

stream = Serial('/dev/ttyACM0', 38400, timeout=1)
out_queue = Queue()
gnr = GNSSReader(stream)

with GNSSNTRIPClient(None) as gnc:
    # start NTRIP client (it should push corrections into out_queue)
    gnc.run(
        server="macorsrtk.massdot.state.ma.us",
        port=10000,
        ntripuser=os.getenv("NTRIP_USER"),
        ntrippassword=os.getenv("NTRIP_PWD"),
        mountpoint="RTCM3MSM_IMAX",
        ggamode=0,
        ggainterval=2,
        output=out_queue,
    )

    while True:
        # 1) write all available RTCM without blocking
        try:
            while True:
                item = out_queue.get_nowait()

                # item might be bytes, or tuple of mixed stuff
                if isinstance(item, (bytes, bytearray, memoryview)):
                    payload = bytes(item)
                elif isinstance(item, tuple):
                    payload = b"".join(
                        p for p in item if isinstance(p, (bytes, bytearray, memoryview))
                    )
                else:
                    payload = b""

                if payload:
                    stream.write(payload)

        except Empty:
            pass

        # 2) read GNSS output
        raw, parsed = gnr.read()
        if parsed is not None and getattr(parsed, "identity", None) == "NAV-PVT":
            rtk_status = {0: "None", 1: "Float", 2: "Fixed"}.get(parsed.carrSoln, "Unknown")
            print(
                f"Fix: {parsed.fixType}D | RTK: {rtk_status} | "
                f"NTRIP Age: {parsed.lastCorrectionAge}s | "
                f"Sats: {parsed.numSV} | "
                f"Lat: {parsed.lat}, Lon: {parsed.lon}"
            )