import cv2
import numpy as np
from ai.vision import find_blobs_hsv
from data_structures import Vision, ThrusterCommands, Sensors
from ai.mission import MissionControl # Now it's a clean, local import

class Submarine:
    def __init__(self, config):
        self.config = config
        self.vision = Vision()
        self.mission_control = MissionControl(config)

    def update(self, dt, sensors):
        if sensors.camera is None:
            return self.mission_control.get_idle_commands(), self.vision

        # Color Conversion
        hsv = cv2.cvtColor(sensors.camera, cv2.COLOR_BGR2HSV)

        # Vision Population (using the tuple unpacking fix)
        self.vision.red_blobs, _ = find_blobs_hsv(hsv, self.config.red_hsv_ranges, self.config.min_gate_pixels)
        self.vision.orange_blobs, _ = find_blobs_hsv(hsv, self.config.orange_hsv_ranges, self.config.min_marker_pixels)
        self.vision.green_blobs, _ = find_blobs_hsv(hsv, self.config.green_hsv_range, self.config.min_gate_pixels)

        # Mission Execution
        status, commands = self.mission_control.execute(self, dt, sensors, self.vision, self.config)

        return commands, self.vision