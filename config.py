# config.py

# OpenCV Standard: H: 0-179, S/V: 0-255
RED_HSV_RANGES = ((0, 100, 100), (10, 255, 255))
GREEN_HSV_RANGE = ((50, 50, 50), (70, 255, 255))

# Global Mission Constants
MIN_GATE_PIXELS = 500
MIN_POLE_PIXELS = 300
MISSION_DEPTH = 1.5

class MissionConfig:
    def __init__(self):
        self.red_hsv_ranges = RED_HSV_RANGES
        self.green_hsv_range = GREEN_HSV_RANGE
        self.min_gate_pixels = MIN_GATE_PIXELS
        self.min_pole_pixels = MIN_POLE_PIXELS
        self.mission_depth = MISSION_DEPTH