from .subtask_base import Subtask, SubtaskStatus
from .common_subtasks import DiveToDepth, AlignToObjectX, DriveUntilTargetLostForward

class GateTask:
    def __init__(self, target_depth=1.5):
        self.target_depth = target_depth
        self.name = "GateTask"
        
        # Clean Callers: No more tolerance_px or legacy flags
        self.subtasks = [
            DiveToDepth(target_depth=self.target_depth),
            AlignToObjectX(target_type='gate', target_x=0.5, threshold=0.05),
            DriveUntilTargetLostForward(target_type='gate', speed=0.4, timeout=8.0)
        ]
        self.current_subtask_index = 0

    def execute(self, sub, dt, sensors, vision_data, config):
        if self.current_subtask_index >= len(self.subtasks):
            return "finished", None
            
        current = self.subtasks[self.current_subtask_index]
        # We pass an empty context dict {} as the 6th argument to match the execute signature
        status, commands = current.execute(sub, dt, sensors, vision_data, config, {})
        
        if status == "finished":
            self.current_subtask_index += 1
            
        return "running", commands