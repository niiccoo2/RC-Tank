import asyncio
import json
import logging
import platform
from aiortc import RTCPeerConnection, RTCSessionDescription, RTCConfiguration, RTCIceServer # type: ignore
from aiortc.contrib.media import MediaPlayer, MediaRelay # type: ignore
from core.config import get_logger
import re

webrtc = get_logger("webrtc")

class WebRTCManager:
    def __init__(self, cam_src="/dev/video0"):
        self.pcs = set()
        self.relay = MediaRelay()
        
        # Determine platform for camera format
        system = platform.system()
        if system == "Windows":
            self.cam_options = {"framerate": "30", "video_size": "320x240"}
            self.cam_format = "dshow"
            self.cam_file = f"video={cam_src}" if "video=" not in str(cam_src) else cam_src
            if isinstance(cam_src, int):
                 self.cam_file = f"video=Integrated Camera"
        else:
            # Linux / Raspberry Pi
            self.cam_options = {"framerate": "30", "video_size": "320x240"}
            self.cam_format = "v4l2"
            # Ensure cam_src is treated as a string for the path construction if it's an int
            src_str = str(cam_src)
            if src_str.startswith("/dev/video"):
                self.cam_file = src_str
            elif src_str.isdigit():
                self.cam_file = f"/dev/video{src_str}"
            else:
                self.cam_file = src_str

        self.webcam = None

    def filter_candidates(self, sdp: str, allow_ip_prefixes: list) -> str:
        filtered_lines = []
        for line in sdp.splitlines():
            if line.startswith("a=candidate:"):
                fields = line.split()
                if len(fields) >= 8:
                    candidate_ip = fields[4]
                    cand_type = None
                    for idx, token in enumerate(fields):
                        if token == "typ" and (idx + 1 < len(fields)):
                            cand_type = fields[idx + 1]
                    # Allow relay (TURN) candidates ALWAYS
                    if cand_type == "relay":
                        filtered_lines.append(line)
                    # Allow host/srflx (direct) but ONLY if in your allowed modem subnet
                    elif cand_type in ("host", "srflx") and any(candidate_ip.startswith(prefix) for prefix in allow_ip_prefixes):
                        filtered_lines.append(line)
                # else: malformed candidate, skip
            else:
                filtered_lines.append(line)
        return "\r\n".join(filtered_lines) + "\r\n"

    def get_webcam(self):
        if self.webcam is None:
            webrtc.debug(f"Opening WebRTC camera: {self.cam_file} [{self.cam_format}]")
            try:
                self.webcam = MediaPlayer(
                    self.cam_file, 
                    format=self.cam_format, 
                    options=self.cam_options
                )
            except Exception as e:
                webrtc.error(f"Error opening camera: {e}")
                return None
        if self.webcam.video is not None:
            return self.relay.subscribe(self.webcam.video)
        else:
            webrtc.error("No video track found in webcam.")
            return None

    async def offer(self, params):
        offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])
        # We accept bitrate but ignore it to ensure stability as requested
        # target_bitrate = params.get("bitrate", 1000) 

        config = RTCConfiguration(
            iceServers=[
                # RTCIceServer(urls="stun:134.209.220.119:3478"), # do droplet
                # RTCIceServer(
                #     urls="turn:134.209.220.119:3478",
                #     username="tank",
                #     credential="tankpass"
                # )
                RTCIceServer(urls="stun:173.48.62.89:3478"), # home-server
                RTCIceServer(
                    urls="turn:173.48.62.89:3478",
                    username="tank",
                    credential="tankpass"
                )
            ]
        )
        pc = RTCPeerConnection(configuration=config)
        self.pcs.add(pc)

        @pc.on("connectionstatechange")
        async def on_connectionstatechange():
            webrtc.debug(f"Connection state is {pc.connectionState}")
            if pc.connectionState == "failed":
                await pc.close()
                self.pcs.discard(pc)
            elif pc.connectionState == "closed":
                self.pcs.discard(pc)

        # Add video track
        video_track = self.get_webcam()
        if video_track:
            pc.addTrack(video_track)

        await pc.setRemoteDescription(offer)
        answer = await pc.createAnswer()
        await pc.setLocalDescription(answer)  # ICE gathering state gets set here

        # Wait for ICE gathering...
        try:
            await asyncio.wait_for(self._wait_for_ice_gathering(pc), timeout=2.0)
        except asyncio.TimeoutError:
            webrtc.warning("ICE gathering timed out, sending partial answer")

        # FILTER candidates here
        allow_ip_prefixes = ["192.168.225."]  # for usb0
        filtered_sdp = self.filter_candidates(pc.localDescription.sdp, allow_ip_prefixes)

        return {
            "sdp": filtered_sdp,
            "type": pc.localDescription.type
        }

    async def _wait_for_ice_gathering(self, pc):
        while pc.iceGatheringState != "complete":
            await asyncio.sleep(0.05)

    async def cleanup(self):
        webrtc.debug("Cleaning up WebRTC connections...")
        coros = [pc.close() for pc in self.pcs]
        await asyncio.gather(*coros)
        self.pcs.clear()
        if self.webcam:
            self.webcam = None # MediaPlayer doesn't have a close? It does, but via container.
