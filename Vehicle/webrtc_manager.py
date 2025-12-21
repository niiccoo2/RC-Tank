import asyncio
import json
import logging
import platform
import re
from aiortc import RTCPeerConnection, RTCSessionDescription
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
            # Force a lower framerate and resolution to naturally limit bitrate
            self.cam_options = {
                "framerate": "15",      # Lower FPS
                "video_size": "320x240", # Keep small resolution
                "pixel_format": "mjpeg"  # Force MJPEG input
            }
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
        # Default to 1000 kbps if not specified
        target_bitrate = params.get("bitrate", 1000) 

        pc = RTCPeerConnection()
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

        # Apply Bitrate Cap via SDP
        if "m=video" in answer.sdp:
            tias_bps = target_bitrate * 1000
            answer.sdp = re.sub(
                r'(m=video.*(?:\r\n|\n))', 
                f'\\1b=AS:{target_bitrate}\r\nb=TIAS:{tias_bps}\r\n', 
                answer.sdp
            )
            print(f"Bitrate cap applied to SDP ({target_bitrate} kbps)")
        else:
            print("Warning: Could not find video section in SDP to apply bitrate cap")

        await pc.setLocalDescription(answer)

        return {
            "sdp": pc.localDescription.sdp,
            "type": pc.localDescription.type
        }

    async def cleanup(self):
        print("Cleaning up WebRTC connections...")
        coros = [pc.close() for pc in self.pcs]
        await asyncio.gather(*coros)
        self.pcs.clear()
        if self.webcam:
            self.webcam = None # MediaPlayer doesn't have a close? It does, but via container.
