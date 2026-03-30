import time
from enum import Enum

class TaskStatus(Enum):
    IDLE = 0
    RUNNING = 1
    FINISHED = 2
    FAILED = 3

class Task:
    def __init__(self):
        self.name = "BaseTask"
        self.status = TaskStatus.IDLE

    def execute(self, sub, dt, sensors, vision_data, config):
        """Must be implemented by subclasses like GateTask."""
        raise NotImplementedError("Tasks must implement execute()")

class MissionControl:
    def __init__(self, mission_file=None):
        self.tasks = []
        self.current_task_index = 0
        self.start_time = time.time()

    def execute(self, sub, dt, sensors, vision_data, config):
        if self.current_task_index >= len(self.tasks):
            return "finished", None

        current_task = self.tasks[self.current_task_index]
        status, commands = current_task.execute(sub, dt, sensors, vision_data, config)

        if status == "finished":
            print(f"[INFO] Completed Task: {current_task.name}")
            self.current_task_index += 1
            if self.current_task_index < len(self.tasks):
                print(f"[INFO] Transitioning to: {self.tasks[self.current_task_index].name}")
        
        return status, commands

    def get_current_task_name(self):
        if self.current_task_index < len(self.tasks):
            return self.tasks[self.current_task_index].name
        return "Mission Complete"