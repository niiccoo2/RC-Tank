import asyncio
import json
import logging
import platform
from aiortc import RTCPeerConnection, RTCSessionDescription, RTCConfiguration, RTCIceServer
from aiortc.contrib.media import MediaPlayer, MediaRelay

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

    def get_webcam(self):
        if self.webcam is None:
            print(f"Opening WebRTC camera: {self.cam_file} [{self.cam_format}]")
            try:
                self.webcam = MediaPlayer(
                    self.cam_file, 
                    format=self.cam_format, 
                    options=self.cam_options
                )
            except Exception as e:
                print(f"Error opening camera: {e}")
                return None
        if self.webcam.video is not None:
            return self.relay.subscribe(self.webcam.video)
        else:
            print("No video track found in webcam.")
            return None

    async def offer(self, params):
        offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])
        # We accept bitrate but ignore it to ensure stability as requested
        # target_bitrate = params.get("bitrate", 1000) 

        config = RTCConfiguration(
            iceServers=[
                RTCIceServer(urls="stun:68.183.59.124:3478"),
                RTCIceServer(
                    urls="turn:68.183.59.124:3478",
                    username="tank",
                    credential="tankpass"
                )
            ]
        )
        pc = RTCPeerConnection(configuration=config)
        self.pcs.add(pc)

        @pc.on("connectionstatechange")
        async def on_connectionstatechange():
            print(f"Connection state is {pc.connectionState}")
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
        await pc.setLocalDescription(answer)

        # Wait for ICE gathering to complete or timeout after 2 seconds
        # This ensures we get STUN/Tailscale candidates without hanging forever
        try:
            await asyncio.wait_for(self._wait_for_ice_gathering(pc), timeout=2.0)
        except asyncio.TimeoutError:
            print("ICE gathering timed out, sending partial answer")

        return {
            "sdp": pc.localDescription.sdp,
            "type": pc.localDescription.type
        }

    async def _wait_for_ice_gathering(self, pc):
        while pc.iceGatheringState != "complete":
            await asyncio.sleep(0.05)

    async def cleanup(self):
        print("Cleaning up WebRTC connections...")
        coros = [pc.close() for pc in self.pcs]
        await asyncio.gather(*coros)
        self.pcs.clear()
        if self.webcam:
            self.webcam = None # MediaPlayer doesn't have a close? It does, but via container.
