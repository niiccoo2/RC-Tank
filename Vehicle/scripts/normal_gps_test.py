from serial import Serial
from queue import Queue, Empty
import os
import time
from dotenv import load_dotenv

from pygnssutils import GNSSNTRIPClient, GNSSReader
from pyubx2 import UBXMessage, SET

load_dotenv()

PORT = "/dev/ttyACM0"
BAUD = 38400  # ignored by USB-CDC on many devices, but harmless

NTRIP_SERVER = "macorsrtk.massdot.state.ma.us"
NTRIP_PORT = 10000
NTRIP_MOUNT = "RTCM3MSM_IMAX"

REFLAT = 42.370152
REFLON = -71.172057
REFALT = 0.0
REFSEP = 0.0


def send_valset(stream: Serial, pairs, layers=1):
    """
    Send UBX-CFG-VALSET.
    layers: 1=RAM, 2=BBR, 4=Flash. Use RAM for safe testing.
    """
    msg = UBXMessage(
        "CFG",
        "CFG-VALSET",
        SET,
        version=0,
        layers=layers,
        transaction=0,
        keys=pairs,
    )
    stream.write(msg.serialize())
    stream.flush()
    time.sleep(0.2)


def configure_ublox_usb_for_rtk(stream: Serial):
    """
    Configure u-blox receiver over USB:
    - allow RTCM3 input on USB
    - output UBX on USB
    - enable NAV-PVT on USB
    RAM-only (won't persist after power cycle).
    """
    pairs = [
        # Accept RTCM3 on USB input
        ("CFG_USBINPROT_UBX", 1),
        ("CFG_USBINPROT_NMEA", 1),
        ("CFG_USBINPROT_RTCM3X", 1),

        # Output UBX on USB (reduce NMEA chatter to keep parsing clean)
        ("CFG_USBOUTPROT_UBX", 1),
        ("CFG_USBOUTPROT_NMEA", 0),
        ("CFG_USBOUTPROT_RTCM3X", 0),

        # Ensure NAV-PVT is emitted on USB so we can watch RTK state
        ("CFG_MSGOUT_UBX_NAV_PVT_USB", 1),
    ]
    send_valset(stream, pairs, layers=1)


def main():
    stream = Serial(PORT, BAUD, timeout=1)

    # 1) Configure receiver so it will actually accept RTCM on USB
    configure_ublox_usb_for_rtk(stream)

    # 2) Start NTRIP client -> queue, and inject RTCM raw bytes into receiver
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
            # Drain NTRIP output and inject corrections
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

            # Read GNSS output and show RTK indicators
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