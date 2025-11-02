from tankClass import Tank
from streamerClass import MJPEGStreamer

from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import time
import atexit
import threading

# Colors (kept as-is)
BLACK = "\033[0;30m"
RED = "\033[0;31m"
GREEN = "\033[0;32m"
BROWN = "\033[0;33m"
BLUE = "\033[0;34m"
PURPLE = "\033[0;35m"
RESET = "\033[0m"

app = Flask(__name__)
CORS(app)

tank = Tank()

streamer = MJPEGStreamer(
    src=0,
    width=160,
    height=120,
    cam_fps=30,
    fourcc_str="MJPG",         # try "YUYV" if MJPG isn't supported well
    rotate_180=True,
    jpeg_quality=45,           # lower => smaller bytes
    motion_gate=True,
    motion_thresh=6.0,
    share_encoded=True         # encode once, share to all clients (lowest CPU)
)
streamer.start()

# --------- ROUTES ----------
@app.route('/camera')
def camera():
    # Optional knobs: /camera?fps=8&q=40
    try:
        fps = int(request.args.get('fps', 12))   # lower FPS => fewer bytes
        fps = max(1, min(30, fps))
    except Exception:
        fps = 12

    q_param = request.args.get('q')  # only used if share_encoded=False
    q_override = int(q_param) if q_param is not None else None

    return Response(
        streamer.gen_frames(max_fps=fps, quality_override=q_override),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )

@app.route('/motor', methods=['POST'])
def set_motor():
    """
    POST /motor
    Body: {"left": -1.0 to 1.0, "right": -1.0 to 1.0}
    """
    tank.last_update_time = time.time()

    data = request.get_json()
    print(f"Received motor command: {data}")
    left_speed = float(data.get('left', 0.0))
    right_speed = float(data.get('right', 0.0))

    tank.set_esc(tank.left, left_speed)
    tank.set_esc(tank.right, right_speed)

    return jsonify({"status": "ok", "left": left_speed, "right": right_speed})

@app.route('/stop', methods=['POST'])
def stop():
    tank.set_esc(tank.left, 0.0)
    tank.set_esc(tank.right, 0.0)
    return jsonify({"status": "stopped"})

# --------- STARTUP / CLEANUP ----------
print("Arming ESCs...")
tank.arm_escs()
print("Ready")

# Clean up motors and streamer on exit
def _cleanup():
    try:
        tank.cleanup()
    finally:
        streamer.stop()

atexit.register(_cleanup)

if __name__ == '__main__':
    t = threading.Thread(target=tank.timeout_check, daemon=True)
    t.start()
    # app.run(host='0.0.0.0', port=5000, ssl_context=('cert.pem', 'key.pem'))
    app.run(host='0.0.0.0', port=5000)
