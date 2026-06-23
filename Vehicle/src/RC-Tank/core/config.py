import argparse
import logging

def _parse_flags():
    parser = argparse.ArgumentParser()
    parser.add_argument('--motor-debug', action='store_true', help='Show motor debug logs')
    parser.add_argument('--compass-debug', action='store_true', help='Show compass debug logs')
    parser.add_argument('--gps-debug', action='store_true', help='Show gps debug logs')
    parser.add_argument('--webrtc-debug', action='store_true', help='Show webrtc debug logs')
    parser.add_argument('--self_driving-debug', action='store_true', help='Show self_driving debug logs')
    parser.add_argument('--websocket-debug', action='store_true', help='Show websocket debug logs')
    parser.add_argument('--lifecycle-debug', action='store_true', help='Show lifecycle debug logs')
    
    return parser.parse_args()

args = _parse_flags()

root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)

log_format = logging.Formatter('[%(levelname)s] %(name)s: %(message)s')

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.WARNING)
console_handler.setFormatter(log_format)
root_logger.addHandler(console_handler)

file_handler = logging.FileHandler('tank.log', mode='a') # 'w' overwrites each run; use 'a' to append
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(log_format)
root_logger.addHandler(file_handler)

# ------------------------------

def get_logger(name):
    """Returns a logger and sets its level based on flags."""
    logger = logging.getLogger(name)
    
    debug_flags = {
        'motor': args.motor_debug,
        'compass': args.compass_debug,
        'gps': args.gps_debug,
        'webrtc': args.webrtc_debug,
        'self_driving': args.self_driving_debug,
        'websocket': args.websocket_debug,
        'lifecycle': args.lifecycle_debug
    }
    
    if name in debug_flags and debug_flags[name]:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.WARNING)
        
    return logger