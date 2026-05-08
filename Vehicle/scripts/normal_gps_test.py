import os
import time
from queue import Queue, Empty
from dotenv import load_dotenv
from serial import Serial

from pygnssutils import GNSSNTRIPClient, GNSSReader

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


def ubx_checksum(payload: bytes) -> bytes:
    ck_a = 0
    ck_b = 0
    for b in payload:
        ck_a = (ck_a + b) & 0xFF
        ck_b = (ck_b + ck_a) & 0xFF
    return bytes([ck_a, ck_b])


def ubx_frame(msg_class: int, msg_id: int, payload: bytes) -> bytes:
    length = len(payload).to_bytes(2, "little")
    body = bytes([msg_class, msg_id]) + length + payload
    return b"\xB5\x62" + body + ubx_checksum(body)


def send_cfg_prt_usb(stream: Serial, in_mask: int, out_mask: int):
    """
    Send UBX-CFG-PRT for USB port (portID=3).

    in_mask/out_mask bits (u-blox):
      bit0 UBX, bit1 NMEA, bit2 RTCM2, bit3 RTCM3, bit4 SPARTN (newer), bit5 UBX+ (etc)
    We care about UBX/NMEA/RTCM3 => bits 0,1,3.
    """

    portID = 3  # USB
    reserved0 = 0

    # For USB, most of these fields are ignored but must be present.
    txReady = 0
    mode = 0
    baudRate = 0
    inProtoMask = in_mask
    outProtoMask = out_mask
    flags = 0
    reserved5 = 0

    payload = (
        bytes([portID, reserved0])
        + txReady.to_bytes(2, "little")
        + mode.to_bytes(4, "little")
        + baudRate.to_bytes(4, "little")
        + inProtoMask.to_bytes(2, "little")
        + outProtoMask.to_bytes(2, "little")
        + flags.to_bytes(2, "little")
        + reserved5.to_bytes(2, "little")
    )

    msg = ubx_frame(0x06, 0x00, payload)  # CFG-PRT
    stream.write(msg)
    stream.flush()
    time.sleep(0.2)


def configure_zedf9p_usb(stream: Serial):
    # input: UBX + NMEA + RTCM3
    IN_UBX = 1 << 0
    IN_NMEA = 1 << 1
    IN_RTCM3 = 1 << 3

    # output: UBX only (set NMEA too if you want, but UBX-only is cleaner for parsing)
    OUT_UBX = 1 << 0
    OUT_NMEA = 0

    send_cfg_prt_usb(stream, in_mask=(IN_UBX | IN_NMEA | IN_RTCM3), out_mask=(OUT_UBX | OUT_NMEA))


def main():
    stream = Serial(PORT, BAUD, timeout=1)

    # 1) Configure receiver to accept RTCM3 on USB and output UBX
    configure_zedf9p_usb(stream)

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
            # inject corrections + print what arrives
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

            # show rover status
            raw_gnss, parsed_gnss = gnr.read()
            if parsed_gnss is not None and getattr(parsed_gnss, "identity", None) == "NAV-PVT":
                rtk_status = {0: "None", 1: "Float", 2: "Fixed"}.get(parsed_gnss.carrSoln, "Unknown")
                print(
                    f"Fix: {parsed_gnss.fixType}D | RTK: {rtk_status} | "
                    f"diffSoln: {parsed_gnss.diffSoln} | corrAge: {parsed_gnss.lastCorrectionAge}s | "
                    f"hAcc: {parsed_gnss.hAcc}mm | Sats: {parsed_gnss.numSV} | "
                    f"Lat: {parsed_gnss.lat}, Lon: {parsed_gnss.lon}"
                )


if __name__ == "__main__":
    main()