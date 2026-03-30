# config.py

# OpenCV Standard: H: 0-179, S/V: 0-255
RED_HSV_RANGES = ((0, 100, 100), (10, 255, 255))
GREEN_HSV_RANGE = ((50, 50, 50), (70, 255, 255))

min_gate_pixels = 500
min_pole_pixels = 300
MISSION_DEPTH = 1.5

class SimulationConfig:
    def __init__(self):
        self.red_hsv_ranges = RED_HSV_RANGES
        self.green_hsv_range = GREEN_HSV_RANGE
        self.min_gate_pixels = min_gate_pixels
        self.min_pole_pixels = min_pole_pixels
        self.mission_depth = MISSION_DEPTH
