from .task_base import Task, TaskStatus

class ShutdownTask(Task):
    def __init__(self):
        super().__init__()
        self.name = "ShutdownTask"

    def execute(self, sub, dt, sensors, vision_data, config):
        """
        The mission is over. Return neutral thruster commands 
        to ensure the sub stops and stays put.
        """
        from data_structures import ThrusterCommands
        # Return neutral commands and 'finished' status
        return "finished", ThrusterCommands(forward=0.0, lateral=0.0, vertical=0.0, yaw=0.0)