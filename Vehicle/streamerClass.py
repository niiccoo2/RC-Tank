import cv2
import time
import threading
from typing import Optional
import numpy as np

def fourcc(code: str) -> int:
    # Helper to keep Pylance happy; equivalent to cv2.VideoWriter_fourcc(*code)
    return cv2.VideoWriter_fourcc(*code) # type: ignore

class MJPEGStreamer:
    def __init__(
        self,
        src: int = 0,
        width: int = 160,
        height: int = 120,
        cam_fps: int = 30,
        fourcc_str: str = "MJPG",       # or "YUYV"
        rotate_180: bool = True,
        jpeg_quality: int = 45,         # 35..55 keeps bytes low
        motion_gate: bool = True,
        motion_thresh: float = 6.0,     # lower = more sensitive
        share_encoded: bool = True      # True = encode once, share to all clients
    ):
        self.width = width
        self.height = height
        self.rotate_180 = rotate_180
        self.motion_gate = motion_gate
        self.motion_thresh = motion_thresh
        self.share_encoded = share_encoded

        # JPEG params (favor small size)
        self.jpeg_params: list[int] = [
            int(cv2.IMWRITE_JPEG_QUALITY), int(jpeg_quality),
            int(cv2.IMWRITE_JPEG_OPTIMIZE), 1,
            int(cv2.IMWRITE_JPEG_PROGRESSIVE), 0
        ]

        # Camera
        self.cap = cv2.VideoCapture(src)
        # Use helper to avoid Pylance attr-defined warning
        self.cap.set(cv2.CAP_PROP_FOURCC, fourcc(fourcc_str))
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self.cap.set(cv2.CAP_PROP_FPS, cam_fps)
        try:
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        except Exception:
            pass

        # Shared state
        self._lock = threading.Lock()
        self._running = False

        # If sharing encoded: latest JPEG; else: latest processed grayscale frame
        self._latest_jpeg: Optional[bytes] = None
        self._latest_small: Optional[np.ndarray] = None
        self._latest_ts: float = 0.0

        self._thr: Optional[threading.Thread] = None

    # ---------- Public API ----------
    def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._thr = threading.Thread(target=self._capture_loop, daemon=True)
        self._thr.start()

    def stop(self) -> None:
        self._running = False
        if self._thr and self._thr.is_alive():
            self._thr.join(timeout=1.0)
        try:
            self.cap.release()
        except Exception:
            pass

    def set_quality(self, q: int) -> None:
        q = max(10, min(95, int(q)))
        with self._lock:
            self.jpeg_params[1] = q  # update IMWRITE_JPEG_QUALITY

    def gen_frames(self, max_fps: int = 12, quality_override: Optional[int] = None):
        """
        Flask generator: yields latest frame with no queue buildup.
        Lower max_fps => fewer bytes. Latency stays low because we always serve 'latest'.
        """
        min_interval = 1.0 / max_fps
        last_send = 0.0

        # Local encode settings (only used if per-client encode)
        if quality_override is not None:
            local_params = self.jpeg_params[:]
            local_params[1] = max(10, min(95, int(quality_override)))
        else:
            local_params = self.jpeg_params

        while True:
            # FPS cap (bandwidth knob)
            now = time.time()
            wait = min_interval - (now - last_send)
            if wait > 0:
                time.sleep(wait)

            if self.share_encoded:
                with self._lock:
                    jpg = self._latest_jpeg
                if jpg is None:
                    continue
                last_send = time.time()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n'
                       b'Content-Length: ' + str(len(jpg)).encode() + b'\r\n\r\n' +
                       jpg + b'\r\n')
            else:
                # Narrow None before copy to satisfy Pylance
                with self._lock:
                    src_small = self._latest_small
                if src_small is None:
                    continue
                small = src_small.copy()
                ok, buf = cv2.imencode('.jpg', small, local_params)
                if not ok:
                    continue
                jpg = buf.tobytes()
                last_send = time.time()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n'
                       b'Content-Length: ' + str(len(jpg)).encode() + b'\r\n\r\n' +
                       jpg + b'\r\n')

    # ---------- Internal capture loop ----------
    def _capture_loop(self) -> None:
        prev_small: Optional[np.ndarray] = None

        while self._running:
            ok, frame = self.cap.read()
            if not ok:
                time.sleep(0.005)
                continue

            if self.rotate_180:
                frame = cv2.rotate(frame, cv2.ROTATE_180)

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # NOTE: camera is already set to width/height; resize is cheap sanity
            small = cv2.resize(gray, (self.width, self.height), interpolation=cv2.INTER_AREA)

            # Motion gating: skip encode if scene barely changed
            if self.motion_gate and prev_small is not None:
                mean_change = float(cv2.absdiff(small, prev_small).mean())
                if mean_change < self.motion_thresh:
                    # Keep previous output; do not overwrite latest or re-encode
                    continue
            prev_small = small

            if self.share_encoded:
                ok, buf = cv2.imencode('.jpg', small, self.jpeg_params)
                if not ok:
                    continue
                jpg_bytes = buf.tobytes()
                with self._lock:
                    self._latest_jpeg = jpg_bytes
                    self._latest_ts = time.time()
            else:
                with self._lock:
                    self._latest_small = small
                    self._latest_ts = time.time()
