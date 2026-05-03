import argparse
import logging

# Set the base logging style for the whole project
logging.basicConfig(level=logging.WARNING, format='[%(levelname)s] %(name)s: %(message)s')

def _parse_flags():
    parser = argparse.ArgumentParser()
    parser.add_argument('--motor-debug', action='store_true', help='Show motor debug logs')
    parser.add_argument('--compass-debug', action='store_true', help='Show compass debug logs')
    parser.add_argument('--gps-debug', action='store_true', help='Show gps debug logs')
    parser.add_argument('--webrtc-debug', action='store_true', help='Show webrtc debug logs')
    parser.add_argument('--self_driving-debug', action='store_true', help='Show self_driving debug logs')
    
    return parser.parse_args()

# Run this once when config.py is imported
args = _parse_flags()

def get_logger(name):
    """Returns a logger and sets its level based on flags."""
    logger = logging.getLogger(name)
    
    # Logic to enable specific debuggers
    if name == 'motor' and args.motor_debug:
        logger.setLevel(logging.DEBUG)
    elif name == 'compass' and args.compass_debug:
        logger.setLevel(logging.DEBUG)
    elif name == 'gps' and args.gps_debug:
        logger.setLevel(logging.DEBUG)
    elif name == 'webrtc' and args.webrtc_debug:
        logger.setLevel(logging.DEBUG)
    elif name == 'self_driving' and args.self_driving_debug:
        logger.setLevel(logging.DEBUG)
        
    return logger
