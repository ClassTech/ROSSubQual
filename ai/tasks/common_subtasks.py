import numpy as np
from data_structures import ThrusterCommands

class DiveToDepth:
    def __init__(self, target_depth):
        self.target_depth = target_depth

    def execute(self, sub, dt, sensors, vision_data, config, context):
        err = self.target_depth - sensors.depth
        if abs(err) < 0.05:
            return "finished", ThrusterCommands()
        return "running", ThrusterCommands(vertical=np.clip(err * 0.8, -1.0, 1.0))

class AlignToObjectX:
    def __init__(self, target_type='gate', target_x=0.5, threshold=0.05):
        self.target_type = target_type
        self.target_x = target_x     # Now matches the GateTask call
        self.threshold = threshold

    def execute(self, sub, dt, sensors, vision_data, config, context):
        w = sensors.camera_width
        if w == 0: return "running", ThrusterCommands()
        
        curr_x_norm = 0
        if self.target_type == 'gate':
            pair = vision_data.get_gate_pair()
            if not pair: return "failed", ThrusterCommands()
            curr_x_norm = ((pair[0]['center_x'] + pair[1]['center_x']) / 2) / w
        
        err = self.target_x - curr_x_norm
        
        if abs(err) < self.threshold:
            return "finished", ThrusterCommands()
            
        return "running", ThrusterCommands(yaw=np.clip(err * 1.5, -0.6, 0.6))

class DriveUntilTargetLostForward:
    def __init__(self, target_type='gate', speed=0.4, timeout=8.0):
        self.target_type = target_type
        self.speed = speed
        self.timeout = timeout
        self.elapsed = 0.0

    def execute(self, sub, dt, sensors, vision_data, config, context):
        self.elapsed += dt
        visible = vision_data.is_gate_visible() if self.target_type == 'gate' else False
        if not visible or self.elapsed > self.timeout:
            return "finished", ThrusterCommands()
        return "running", ThrusterCommands(forward=self.speed)

# --- Stubs for the remaining imports in __init__.py ---
class TurnToHeading:
    def __init__(self, target_heading): self.target_heading = target_heading
    def execute(self, *args): return "finished", ThrusterCommands()

class DriveStraight:
    def __init__(self, duration, speed): self.d, self.s, self.e = duration, speed, 0.0
    def execute(self, sub, dt, *args):
        self.e += dt
        return ("finished", ThrusterCommands()) if self.e >= self.d else ("running", ThrusterCommands(forward=self.s))

class SwayStraight:
    def __init__(self, duration, speed): self.d, self.s, self.e = duration, speed, 0.0
    def execute(self, sub, dt, *args):
        self.e += dt
        return ("finished", ThrusterCommands()) if self.e >= self.d else ("running", ThrusterCommands(lateral=self.s))

class Stabilize:
    def __init__(self, duration=2.0): self.d, self.e = duration, 0.0
    def execute(self, sub, dt, *args):
        self.e += dt
        return ("finished", ThrusterCommands()) if self.e >= self.d else ("running", ThrusterCommands())

class WaitForTargetVisible:
    def __init__(self, target_type='gate', timeout=10.0): self.t, self.to, self.e = target_type, timeout, 0.0
    def execute(self, sub, dt, sensors, vision, *args):
        self.e += dt
        if vision.is_gate_visible(): return "finished", ThrusterCommands()
        return ("failed", ThrusterCommands()) if self.e > self.to else ("running", ThrusterCommands())

class DriveUntilTargetLost: pass
class SwayUntilTargetLost: pass
class ApproachAndCenterObject: pass
class DynamicOrbitPole: pass