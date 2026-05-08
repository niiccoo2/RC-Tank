from serial import Serial
from queue import Queue, Empty
import os
from dotenv import load_dotenv

from pygnssutils import GNSSNTRIPClient, GNSSReader

from pyubx2 import UBXConfig

load_dotenv()

PORT = "/dev/ttyACM0"
BAUD = 38400

NTRIP_SERVER = "macorsrtk.massdot.state.ma.us"
NTRIP_PORT = 10000
NTRIP_MOUNT = "RTCM3MSM_IMAX"

REFLAT = 42.370152
REFLON = -71.172057
REFALT = 0.0
REFSEP = 0.0


def configure_f9p_usb(stream: Serial):
    """
    Configure ZED-F9P over USB to accept RTCM3 and output UBX NAV-PVT.
    RAM-only by default (won't persist after power cycle).
    """
    cfg = UBXConfig(stream)

    # These are u-blox configuration database keys.
    # UBXConfig will wrap them into CFG-VALSET correctly for your pyubx2 version.
    cfg.set(
        layers="RAM",
        transaction=0,
        cfgdict={
            "CFG_USBINPROT_UBX": 1,
            "CFG_USBINPROT_NMEA": 1,
            "CFG_USBINPROT_RTCM3X": 1,

            "CFG_USBOUTPROT_UBX": 1,
            "CFG_USBOUTPROT_NMEA": 0,
            "CFG_USBOUTPROT_RTCM3X": 0,

            "CFG_MSGOUT_UBX_NAV_PVT_USB": 1,
        },
    )


def main():
    stream = Serial(PORT, BAUD, timeout=1)

    # 1) Configure receiver
    configure_f9p_usb(stream)

    # 2) Start NTRIP + inject RTCM
    out_queue = Queue()
    gnr = GNSSReader(stream)

    with GNSSNTRIPClient(None) as gnc:
        gnc.run(
            server=NTRIP_SERVER,
            port=NTRIP_PORT,
            mountpoint=NTRIP_MOUNT,
            datatype="RTCM",
            ntripuser=os.getenv("NTRIP_USER"),
            ntrippassword=os.getenv("NTRIP_PWD"),
            ggainterval=10,
            ggamode=1,
            reflat=REFLAT,
            reflon=REFLON,
            refalt=REFALT,
            refsep=REFSEP,
            output=out_queue,
        )

        while True:
            try:
                while True:
                    raw, parsed = out_queue.get_nowait()
                    ident = getattr(parsed, "identity", type(parsed).__name__)
                    print(f"NTRIP: {ident} ({len(raw)} bytes)")
                    if raw:
                        stream.write(raw)
                    out_queue.task_done()
            except Empty:
                pass

            raw_gnss, parsed_gnss = gnr.read()
            if parsed_gnss is not None and getattr(parsed_gnss, "identity", None) == "NAV-PVT":
                rtk_status = {0: "None", 1: "Float", 2: "Fixed"}.get(parsed_gnss.carrSoln, "Unknown")
                print(
                    f"Fix: {parsed_gnss.fixType}D | RTK: {rtk_status} | "
                    f"diffSoln: {parsed_gnss.diffSoln} | "
                    f"corrAge: {parsed_gnss.lastCorrectionAge}s | "
                    f"hAcc: {parsed_gnss.hAcc}mm | "
                    f"Sats: {parsed_gnss.numSV} | "
                    f"Lat: {parsed_gnss.lat}, Lon: {parsed_gnss.lon}"
                )


if __name__ == "__main__":
    main()