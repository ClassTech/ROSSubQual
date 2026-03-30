#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, Imu, FluidPressure
from cv_bridge import CvBridge

# Import your existing simulation logic
from ai.submarine import Submarine
from ai.tasks import GateTask, StabilizeTask, OrbitTurnTask, ShutdownTask
from data_structures import SensorSuite, MPU6050Readings

class SubmarineBrainNode(Node):
    def __init__(self):
        super().__init__('sub_brain_node')
        self.bridge = CvBridge()
        
        # 1. Recreate the mission plan from main.py
        MISSION_DEPTH = 1.5
        mission = [
            GateTask(target_depth=MISSION_DEPTH),
            StabilizeTask(duration=2.0, target_depth=MISSION_DEPTH),
            OrbitTurnTask(target_depth=MISSION_DEPTH, orbit_yaw_gain=4.5, orbit_sway_power=-0.5),
            GateTask(target_depth=MISSION_DEPTH),
            ShutdownTask()
        ]
        
        self.sub_ai = Submarine(mission_plan=mission)
        self.latest_sensors = SensorSuite(camera_image=None, depth=0.0, heading=0.0, pitch=0.0, 
                                          imu=MPU6050Readings())

        # 2. Subscriptions to Mock (or real) Sensor Nodes
        self.create_subscription(FluidPressure, '/sensors/depth', self.depth_callback, 10)
        self.create_subscription(Imu, '/sensors/imu', self.imu_callback, 10)
        self.create_subscription(Image, '/sensors/camera', self.image_callback, 10)

        # 3. Main AI Loop (Matching the simulator's 60Hz)
        self.timer = self.create_timer(1.0/60.0, self.control_loop)
        self.get_logger().info("Submarine Brain Node Started")

    def depth_callback(self, msg):
        # Conversion based on water density
        self.latest_sensors.depth = msg.fluid_pressure / (1025 * 9.81)

    def imu_callback(self, msg):
        # Map ROS Imu to the AI's internal IMU structure
        self.latest_sensors.imu.gyro_z = msg.angular_velocity.z
        self.latest_sensors.imu.gyro_y = msg.angular_velocity.y

    def image_callback(self, msg):
        # Convert ROS Image to OpenCV format for vision.py
        self.latest_sensors.camera_image = self.bridge.imgmsg_to_cv2(msg, "bgr8")

    def control_loop(self):
        # Log status every 2 seconds if we are stuck
        if not hasattr(self, '_loop_count'): self._loop_count = 0
        self._loop_count += 1
        
        if self._loop_count % 120 == 0: # 60Hz * 2 seconds
            self.get_logger().info(
                f"Status Check - Depth: {self.latest_sensors.depth:.2f}, "
                f"Cam: {'OK' if self.latest_sensors.camera_image is not None else 'MISSING'}"
            )

        if self.latest_sensors.camera_image is None:
            return
    def image_callback(self, msg):
    # Add this line to verify data is arriving
        self.get_logger().info("IMAGE RECEIVED") 
        self.latest_sensors.camera_image = self.bridge.imgmsg_to_cv2(msg, "bgr8")

def main(args=None):
    rclpy.init(args=args)
    node = SubmarineBrainNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
