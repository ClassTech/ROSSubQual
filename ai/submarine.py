import time
from data_structures import ThrusterCommands, Vision
import config

class Submarine:
    def __init__(self, mission_file=None):
        self.config = config.SimulationConfig()
        self.vision = Vision()
        # Ensure your MissionControl logic is imported here
        from ai.tasks.task_base import MissionControl
        self.mission_control = MissionControl(mission_file)

    def update(self, dt, sensors):
        from ai.vision import find_blobs_hsv
        
        # Update Vision Data
        self.vision.red_blobs = find_blobs_hsv(
            sensors.camera_image, config.RED_HSV_RANGES, config.min_gate_pixels
        )
        self.vision.green_blobs = find_blobs_hsv(
            sensors.camera_image, config.GREEN_HSV_RANGE, config.min_pole_pixels
        )

        status, commands = self.mission_control.execute(
            self, dt, sensors, self.vision, self.config
        )
        return commands if commands else ThrusterCommands(), self.vision

    def get_current_state_name(self):
        return self.mission_control.get_current_task_name()
