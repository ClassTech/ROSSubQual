import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Image, LaserScan
from geometry_msgs.msg import Twist
from cv_bridge import CvBridge
from sensor_msgs.msg import CompressedImage
from std_msgs.msg import Float32
import cv2
import time
import numpy as np

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
        
                # Assuming depth comes from a specific sensor or state topic
        # Change the type to CompressedImage and update the topic string
        self.cam_sub = self.create_subscription(CompressedImage, '/camera/image_raw/compressed', self.image_callback, qos_profile_sensor_data)
        self.depth_sub = self.create_subscription( Float32,  '/depth', self.depth_callback, 10)

        # 4. Main Control Loop (10Hz)
        self.timer = self.create_timer(0.1, self.control_loop)
        
        self.get_logger().info("Node Initialized. Waiting for Camera...")

    def image_callback(self, msg):
        try:
            import numpy as np
            import cv2
            
            np_arr = np.frombuffer(msg.data, np.uint8)
            frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            
            if frame is not None:
                self.sensors.camera = frame
                # Automatically set width and height based on the actual pixels
                self.sensors.camera_height, self.sensors.camera_width = frame.shape[:2]
                self.camera_received = True 
            
        except Exception as e:
            print(f"Callback Crash: {e}")
            
    def depth_callback(self, msg):
        # Meters in, meters out. 
        self.sensors.depth = msg.data
        
    def control_loop(self):
        print("CHECKPOINT 1: Timer fired.") # Does the loop even start?
        
        if not self.camera_received:
            self.get_logger().warn("Awaiting Camera...", once=True)
            return
            
        print("CHECKPOINT 2: Camera flag passed.") # Did the image_callback actually unlock us?

        # Calculate Delta Time
        now = self.get_clock().now()
        dt = (now - self.last_time).nanoseconds / 1e9
        self.last_time = now
        
        self.sensors.time = time.time()
        
        # If you added a depth check earlier, it might be trapping you here:
        # if self.sensors.depth is None:
        #     return
        
        print("CHECKPOINT 3: Calling Brain Update...") # Are we crashing right before the call?

        # Get Commands from the Brain (Submarine)
        commands, vision = self.submarine.update(dt, self.sensors)

        # Translate AI commands to ROS2 Twist message
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