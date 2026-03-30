#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, Imu, FluidPressure
import numpy as np
import cv2
from cv_bridge import CvBridge

class MockSensorNode(Node):
    def __init__(self):
        super().__init__('mock_sensor_node')
        self.bridge = CvBridge()
        self.depth_pub = self.create_publisher(FluidPressure, '/sensors/depth', 10)
        self.imu_pub = self.create_publisher(Imu, '/sensors/imu', 10)
        self.image_pub = self.create_publisher(Image, '/sensors/camera', 10)
        
        # Frequency set to 10Hz for mock data
        self.timer = self.create_timer(0.1, self.publish_mock_data)
        self.current_depth = 0.0
        self.get_logger().info("Mock Sensor Node initialized and publishing...")

    def publish_mock_data(self):
        # 1. Simulate gradual diving
        if self.current_depth < 1.5:
            self.current_depth += 0.05
        
        dp_msg = FluidPressure()
        dp_msg.fluid_pressure = self.current_depth * 1025 * 9.81
        self.depth_pub.publish(dp_msg)

        # 2. Simulate stable IMU
        imu_msg = Imu()
        imu_msg.angular_velocity.z = 0.0
        self.imu_pub.publish(imu_msg)

        # 3. Generate Mock Image (Gate)
        img = np.zeros((240, 320, 3), dtype=np.uint8)
        img[:] = (120, 50, 20) # Blue water
        cv2.rectangle(img, (100, 50), (110, 200), (0, 0, 255), -1) # Red Pole 1
        cv2.rectangle(img, (210, 50), (220, 200), (0, 0, 255), -1) # Red Pole 2
        
        img_msg = self.bridge.cv2_to_imgmsg(img, "bgr8")
        self.image_pub.publish(img_msg)

# CRITICAL: This block is required for the docker command to work
def main(args=None):
    rclpy.init(args=args)
    node = MockSensorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
