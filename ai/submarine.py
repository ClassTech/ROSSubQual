import time
from data_structures import ThrusterCommands, Vision
import config

class Submarine:
    def __init__(self, mission_file=None):
        # Using the renamed class from config.py
        self.config = config.MissionConfig()
        self.vision = Vision()
        
        # Late import to prevent circular dependency
        from ai.tasks.task_base import MissionControl
        self.mission_control = MissionControl(mission_file)

    def update(self, dt, sensors):
        from ai.vision import find_blobs_hsv
        
        # Update vision state using MissionConfig parameters
        self.vision.red_blobs = find_blobs_hsv(
            sensors.camera_image, 
            self.config.red_hsv_ranges, 
            self.config.min_gate_pixels
        )
        self.vision.green_blobs = find_blobs_hsv(
            sensors.camera_image, 
            self.config.green_hsv_range, 
            self.config.min_pole_pixels
        )

        # Run mission logic and return resulting thruster commands
        status, commands = self.mission_control.execute(
            self, dt, sensors, self.vision, self.config
        )
        
        return commands if commands else ThrusterCommands(), self.vision

    def get_current_state_name(self):
        return self.mission_control.get_current_task_name()