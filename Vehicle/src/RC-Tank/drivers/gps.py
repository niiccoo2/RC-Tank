import time
from time import sleep
from core.types import Location
from core import states
from core.config import get_logger
import os
from queue import Queue, Empty
from dotenv import load_dotenv
from serial import Serial
from pygnssutils import GNSSNTRIPClient, GNSSReader
from pyubx2 import UBXMessage

load_dotenv()

PORT = "/dev/ttyACM0"
BAUD = 38400

# MaCORS
# NTRIP_SERVER = "macorsrtk.massdot.state.ma.us"
# NTRIP_PORT = 10000
# NTRIP_MOUNT = "RTCM3MSM_IMAX"

# Free trial
NTRIP_SERVER = "rtk.rtkdata.com"
NTRIP_PORT = 2101
NTRIP_MOUNT = "AUTO"

# generic coords for boston
REFLAT = 42.361145
REFLON = -71.057083
REFALT = 0.0
REFSEP = 0.0

class RoverContext:
    def __init__(self):
        # Default starting position (optional, prevents sending 0,0 initially)
        self.lat = REFLAT
        self.lon = REFLON
        self.alt = REFALT
        self.sep = REFSEP
        self.sats = 15

    def get_coordinates(self):
        """GNSSNTRIPClient calls this method every `ggainterval` seconds."""
        # pygnssutils expects a dict for PyGPSClient >= 1.4.20 compatibility
        return {
            "lat": self.lat,
            "lon": self.lon,
            "alt": self.alt,
            "sep": self.sep,
            "sip": self.sats,
            "fix": "3D"
        }

gps = get_logger("gps")

class GPS:
    def __init__(self, port: str = PORT, baud: int = BAUD):
        gps.debug("Initializing GPS")
        self.stream = Serial(PORT, BAUD, timeout=1)

        # Configure receiver to accept RTCM3 on USB and output UBX/NMEA
        self._configure_zedf9p_usb(self.stream)

        self.out_queue = Queue()
        self.gnr = GNSSReader(self.stream)

        # Instantiate the context to hold live coordinates
        self.rover = RoverContext()

    def _configure_zedf9p_usb(self, stream: Serial):
        """
        Configure ZED-F9P via UBX-CFG-VALSET (Generation 9 compatible)
        Ensures RTCM3 is accepted on USB, and NMEA/UBX are output on USB.
        """
        layers = 1  # 1 = RAM
        transaction = 0
        
        # Configure USB Port Protocol In/Out Masks
        cfg_data = [
            ("CFG_USBINPROT_UBX", 1),
            ("CFG_USBINPROT_NMEA", 1),
            ("CFG_USBINPROT_RTCM3X", 1),    # VERY IMPORTANT: Accept RTCM3 on USB
            ("CFG_USBOUTPROT_UBX", 1),
            ("CFG_USBOUTPROT_NMEA", 1),     # Enabled so NTRIP Client can fetch GGA if needed
            ("CFG_USBOUTPROT_RTCM3X", 0),
            
            # Ensure standard messages are output over USB
            ("CFG_MSGOUT_UBX_NAV_PVT_USB", 1),
            ("CFG_MSGOUT_NMEA_ID_GGA_USB", 1),
        ]

        msg = UBXMessage.config_set(layers, transaction, cfg_data) # type: ignore
        stream.write(msg.serialize()) # type: ignore
        stream.flush()
        time.sleep(0.5)
    
    def update_gps_thread(self):
        with GNSSNTRIPClient(self.rover) as gnc:
            gnc.run(
                server=NTRIP_SERVER,
                port=NTRIP_PORT,
                mountpoint=NTRIP_MOUNT,
                datatype="RTCM",
                ntripuser=os.getenv("NTRIP_USER", "anon"),
                ntrippassword=os.getenv("NTRIP_PWD", "password"),
                ggainterval=10,
                ggamode=0, # use live location from gps
                output=self.out_queue,
            )

            while True:
                # inject corrections + print what arrives
                try:
                    while True:
                        raw, parsed = self.out_queue.get_nowait()
                        ident = getattr(parsed, "identity", type(parsed).__name__)
                        # print(f"NTRIP: {ident} ({len(raw)} bytes)")
                        if raw:
                            self.stream.write(raw)
                        self.out_queue.task_done()
                except Empty:
                    pass

                # show rover status
                raw_gnss, parsed_gnss = self.gnr.read()
                if parsed_gnss is not None and getattr(parsed_gnss, "identity", None) == "NAV-PVT":
                    
                    # Update the live coordinates so the NTRIP client can use them!
                    self.rover.lat = parsed_gnss.lat
                    self.rover.lon = parsed_gnss.lon
                    self.rover.sats = parsed_gnss.numSV
                    # hMSL is in mm, convert to meters
                    self.rover.alt = getattr(parsed_gnss, "hMSL", 0.0) / 1000.0
                    
                    rtk_status = {0: "None", 1: "Float", 2: "Fixed"}.get(parsed_gnss.carrSoln, "Unknown")
                    gps.debug(
                        f"Fix: {parsed_gnss.fixType}D | RTK: {rtk_status} | "
                        f"diffSoln: {parsed_gnss.diffSoln} | corrAge: {parsed_gnss.lastCorrectionAge}s | "
                        f"hAcc: {parsed_gnss.hAcc}mm | Sats: {parsed_gnss.numSV} | "
                        f"Lat: {parsed_gnss.lat}, Lon: {parsed_gnss.lon}"
                    )

                    states.gps_location = Location(lat = self.rover.lat, lon = self.rover.lon, alt = self.rover.alt)
                    states.ntrip_status = { 
                        "fix_type": parsed_gnss.fixType, # int
                        "rtk": rtk_status, # string
                        "diff_soln": parsed_gnss.diffSoln, # int, if it is solving
                        "corr_age": parsed_gnss.lastCorrectionAge, # int
                        "h_acc": parsed_gnss.hAcc, # int
                        "sats": parsed_gnss.numSV # int, number sats
                        }

                sleep(.1) # random number, just don't want to be hogging resources