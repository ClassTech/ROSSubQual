import rclpy
from data_structures import ThrusterCommands
from ai.tasks.gate_task import GateTask  # Ensure this path exists

class MissionControl:
    def __init__(self, config):
        self.config = config
        # Initial task for pre-qualification/mission
        self.current_task = GateTask(config)
        self.mission_name = "GateTask"

    def execute(self, sub, dt, sensors, vision_data, config):
        """
        Runs the logic for the current mission state.
        """
        if self.current_task is None:
            return "FINISHED", ThrusterCommands()

        # Execute the specific task (e.g., GateTask)
        status, commands = self.current_task.execute(sub, dt, sensors, vision_data, config)

        # Log status every second for debugging
        if int(sensors.time * 10) % 10 == 0:
            print(f"[INFO] MISSION: {self.mission_name} | Depth: {sensors.depth:.2f}m | Status: {status}")

        return status, commands

    def get_idle_commands(self):
        """Returns zero thrust if sensors are missing."""
        return ThrusterCommands()

    def reset(self):
        self.current_task = GateTask(self.config)