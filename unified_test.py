import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Image, LaserScan
from geometry_msgs.msg import Twist
from cv_bridge import CvBridge
import cv2
import time

# Local Imports
from config import config
from ai.submarine import Submarine
from data_structures import Sensors

class UnifiedSubNode(Node):
    def __init__(self):
        super().__init__('sub_ai_node')
        
        # 1. Initialize Submarine with the config instance
        self.submarine = Submarine(config)
        self.bridge = CvBridge()
        
        # 2. State tracking
        self.last_time = self.get_clock().now()
        self.sensors = Sensors()
        self.camera_received = False

        # 3. ROS2 Publishers & Subscribers
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        
        # Subscribe to camera and depth (simulated or real)
        self.create_subscription(Image, '/camera/image_raw', self.camera_callback, qos_profile_sensor_data)
        # Assuming depth comes from a specific sensor or state topic
        # self.create_subscription(LaserScan, '/scan', self.depth_callback, 10)

        # 4. Main Control Loop (10Hz)
        self.timer = self.create_timer(0.1, self.control_loop)
        
        self.get_logger().info("Node Initialized. Waiting for Camera...")

    def camera_callback(self, msg):
        try:
            # Convert ROS Image to OpenCV BGR
            self.sensors.camera = self.bridge.imgmsg_to_cv2(msg, "bgr8")
            self.camera_received = True
        except Exception as e:
            self.get_logger().error(f"Camera conversion failed: {e}")

    def control_loop(self):
        if not self.camera_received:
            self.get_logger().warn("Awaiting Camera QoS Handshake...", once=True)
            return

        # Calculate Delta Time
        now = self.get_clock().now()
        dt = (now - self.last_time).nanoseconds / 1e9
        self.last_time = now
        
        # Update sensor time/depth (Mocking depth for prequal if sensor missing)
        self.sensors.time = time.time()
        # In a real run, self.sensors.depth would be updated by a subscriber
        
        # 5. Get Commands from the Brain (Submarine)
        # This calls the update() method we just finished in submarine.py
        commands, vision = self.submarine.update(dt, self.sensors)

        # 6. Translate AI commands to ROS2 Twist message
        msg = Twist()
        msg.linear.x = float(commands.forward)
        msg.linear.y = float(commands.lateral)
        msg.linear.z = float(commands.vertical)
        msg.angular.z = float(commands.yaw)
        
        self.cmd_pub.publish(msg)

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