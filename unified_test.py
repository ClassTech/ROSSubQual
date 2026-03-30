#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, Imu, FluidPressure
from cv_bridge import CvBridge
import numpy as np
import cv2

# Import your existing AI
from ai.submarine import Submarine
from ai.tasks import GateTask, StabilizeTask, ShutdownTask

class UnifiedSubNode(Node):
    def __init__(self):
        super().__init__('unified_sub_node')
        self.bridge = CvBridge()
        
        # 1. Setup AI
        mission = [GateTask(target_depth=1.5), ShutdownTask()]
        self.sub_ai = Submarine(mission_plan=mission)
        self.latest_sensors = None # Start as None to prove we receive data

        # 2. Setup Internal "Mock" Publisher
        self.pub_timer = self.create_timer(0.1, self.publish_mock_internally)
        self.depth_pub = self.create_publisher(FluidPressure, '/sensors/depth', 10)
        self.image_pub = self.create_publisher(Image, '/sensors/camera', 10)

        # 3. Setup Internal "Brain" Subscriber
        self.create_subscription(FluidPressure, '/sensors/depth', self.depth_cb, 10)
        self.create_subscription(Image, '/sensors/camera', self.image_cb, 10)

        # 4. Control Loop (60Hz)
        self.create_timer(1.0/60.0, self.control_loop)
        self.current_depth = 0.0
        self.get_logger().info("Unified Test Node Started")

    def publish_mock_internally(self):
        self.current_depth = min(1.5, self.current_depth + 0.05)
        dp = FluidPressure()
        dp.fluid_pressure = self.current_depth * 1025 * 9.81
        self.depth_pub.publish(dp)

        # Create the "Gate" with two red poles
        img = np.zeros((240, 320, 3), dtype=np.uint8)
        img[:] = (120, 50, 20) # Blue water
        
        # Pole 1 (Left)
        cv2.rectangle(img, (100, 50), (110, 200), (0, 0, 255), -1) 
        # Pole 2 (Right) - ADD THIS LINE
        cv2.rectangle(img, (210, 50), (220, 200), (0, 0, 255), -1) 
        
        self.image_pub.publish(self.bridge.cv2_to_imgmsg(img, "bgr8"))

    def depth_cb(self, msg):
        if self.latest_sensors is None: 
                from data_structures import SensorSuite, MPU6050Readings
                # Using named arguments ensures Python puts the data in the right slots
                self.latest_sensors = SensorSuite(
                camera_image=None, 
                x=0.0, 
                y=0.0, 
                depth=0.0, 
                heading=0.0, 
                pitch=0.0, 
                imu=MPU6050Readings()
                )
    
        # Calculate depth from pressure
        self.latest_sensors.depth = msg.fluid_pressure / (1025 * 9.81)

    def image_cb(self, msg):
        if self.latest_sensors:
            self.latest_sensors.camera_image = self.bridge.imgmsg_to_cv2(msg, "bgr8")

    def control_loop(self):
        if self.latest_sensors and self.latest_sensors.camera_image is not None:
            cmd, vision = self.sub_ai.update(1.0/60.0, self.latest_sensors)
            
            # --- ADD THESE DEBUG LOGS ---
            red_count = len(vision.red_blobs)
            current_subtask = self.sub_ai.get_current_state_name()
            
            self.get_logger().info(
                f"Depth: {self.latest_sensors.depth:.2f} | "
                f"Task: {current_subtask} | "
                f"Red Blobs: {red_count}"
            )
def main():
    rclpy.init()
    rclpy.spin(UnifiedSubNode())
    rclpy.shutdown()

if __name__ == '__main__':
    main()
