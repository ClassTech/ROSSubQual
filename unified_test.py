#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, FluidPressure, Imu
from geometry_msgs.msg import PoseStamped, Twist
from cv_bridge import CvBridge
import numpy as np
from rclpy.qos import qos_profile_sensor_data

from ai.submarine import Submarine
from ai.tasks import GateTask, ShutdownTask
from data_structures import SensorSuite, ThrusterCommands

class UnifiedSubNode(Node):
    def __init__(self):
        super().__init__('sub_ai_node')
        self.bridge = CvBridge()
        self.submarine = Submarine()
        
        self.submarine.mission_control.tasks = [
            GateTask(target_depth=1.5),
            ShutdownTask()
        ]

        # Subscribers
        self.create_subscription(
            Image, 
            '/thwaites/camera/image_raw', 
            self.image_callback, 
            qos_profile_sensor_data  # Use the sensor-specific profile
            )
        self.create_subscription(FluidPressure, '/thwaites/pressure', self.pressure_callback, 10)
        self.create_subscription(PoseStamped, '/thwaites/ground_truth', self.pose_callback, 10)

        # Publisher
        self.cmd_pub = self.create_publisher(Twist, '/thwaites/cmd_vel', 10)

        # State
        self.current_image = None
        self.current_depth = 0.0
        self.current_heading = 0.0
        self.last_time = self.get_clock().now()

        # Timer
        self.timer = self.create_timer(0.05, self.control_loop)
        self.get_logger().info("--- Node Initialized: Awaiting Data Streams ---")

    def image_callback(self, msg):
        try:
            self.current_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
            # Log only the first time we get an image
            if not hasattr(self, '_first_img'):
                self.get_logger().info("SUCCESS: Camera data stream active.")
                self._first_img = True
        except Exception as e:
            self.get_logger().error(f"Image Conversion Error: {e}")

    def pressure_callback(self, msg):
        # Convert Pascal to Meters
        self.current_depth = (msg.fluid_pressure - 101325.0) / 9806.65
        if not hasattr(self, '_first_depth'):
            self.get_logger().info("SUCCESS: Pressure data stream active.")
            self._first_depth = True

    def pose_callback(self, msg):
        q = msg.pose.orientation
        siny_cosp = 2 * (q.w * q.z + q.x * q.y)
        cosy_cosp = 1 - 2 * (q.y * q.y + q.z * q.z)
        self.current_heading = np.degrees(np.arctan2(siny_cosp, cosy_cosp))

    def control_loop(self):
        # Diagnostic Heartbeat
        if self.current_image is None:
            self.get_logger().warn("WAITING: No camera image yet...", throttle_duration_sec=2.0)
            return

        now = self.get_clock().now()
        dt = (now - self.last_time).nanoseconds / 1e9
        self.last_time = now

        sensors = SensorSuite(
            camera_image=self.current_image,
            depth=self.current_depth,
            heading=self.current_heading
        )

        commands, vision = self.submarine.update(dt, sensors)

        twist = Twist()
        twist.linear.x = float(commands.forward)
        twist.linear.y = float(commands.lateral)
        twist.linear.z = float(commands.vertical)
        twist.angular.z = float(commands.yaw)
        self.cmd_pub.publish(twist)

        # Force status output to the logs
        task_name = self.submarine.get_current_state_name()
        self.get_logger().info(f"STATUS: {task_name} | Depth: {self.current_depth:.2f}m", throttle_duration_sec=1.0)

def main(args=None):
    rclpy.init(args=args)
    node = UnifiedSubNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()