import numpy as np
from data_structures import ThrusterCommands

class DiveToDepth:
    def __init__(self, target_depth):
        self.target_depth = target_depth

    def execute(self, sub, dt, sensors, vision_data, config, context):
        error = self.target_depth - sensors.depth
        if abs(error) < 0.05:
            return "finished", ThrusterCommands()
        
        cmds = ThrusterCommands()
        cmds.vertical = np.clip(error * 0.8, -1.0, 1.0)
        return "running", cmds

class WaitForTargetVisible:
    def __init__(self, target_type='gate', timeout=10.0):
        self.target_type = target_type
        self.elapsed = 0.0
        self.timeout = timeout

    def execute(self, sub, dt, sensors, vision_data, config, context):
        self.elapsed += dt
        visible = False
        if self.target_type == 'gate':
            visible = vision_data.is_gate_visible()
            
        if visible: return "finished", ThrusterCommands()
        if self.elapsed > self.timeout: return "failed", ThrusterCommands()
        return "running", ThrusterCommands()

class AlignToObjectX:
    def __init__(self, target_type='gate', target_x_fraction=0.5):
        self.target_type = target_type
        self.target_x_fraction = target_x_fraction

    def execute(self, sub, dt, sensors, vision_data, config, context):
        cam_w = sensors.camera_width
        if cam_w == 0: return "running", ThrusterCommands()

        target_x = cam_w * self.target_x_fraction
        current_x = 0
        
        if self.target_type == 'gate':
            pair = vision_data.get_gate_pair()
            if not pair: return "failed", ThrusterCommands()
            current_x = (pair[0]['center_x'] + pair[1]['center_x']) / 2
        
        error = (target_x - current_x) / cam_w
        cmds = ThrusterCommands()
        cmds.yaw = np.clip(error * 1.5, -1.0, 1.0)
        
        if abs(error) < 0.05: return "finished", cmds
        return "running", cmds

class DriveForward:
    def __init__(self, duration=3.0, speed=0.4):
        self.duration = duration
        self.speed = speed
        self.elapsed = 0.0

    def execute(self, sub, dt, sensors, vision_data, config, context):
        self.elapsed += dt
        if self.elapsed >= self.duration:
            return "finished", ThrusterCommands()
        return "running", ThrusterCommands(forward=self.speed)

class SwayStraight:
    def __init__(self, duration=2.0, speed=0.3):
        self.duration = duration
        self.speed = speed
        self.elapsed = 0.0

    def execute(self, sub, dt, sensors, vision_data, config, context):
        self.elapsed += dt
        if self.elapsed >= self.duration:
            return "finished", ThrusterCommands()
        # Maintains heading while moving laterally
        return "running", ThrusterCommands(lateral=self.speed)
