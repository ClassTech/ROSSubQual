#!/usr/bin/env python3
import math
import time
import numpy as np
import pygame
import rclpy
import cv2
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from geometry_msgs.msg import Twist
from cv_bridge import CvBridge
from sensor_msgs.msg import CompressedImage
from std_msgs.msg import Float32

# Explicitly sourced from your config
from config import *
from world import SubmarinePhysicsState, PrequalGate, PrequalMarker
from data_structures import ThrusterCommands

class SubmarineSimulator(Node):
    def __init__(self, width=1200, height=800):
        super().__init__('simulator_node')
        self.bridge = CvBridge()
        
        # ROS2 Communication
        self.image_pub = self.create_publisher(CompressedImage, '/camera/image_raw/compressed', qos_profile_sensor_data)
        self.depth_pub = self.create_publisher(Float32, '/depth', 10)
        self.create_subscription(Twist, '/cmd_vel', self.cmd_callback, 10)
        
        # Simulation Constants
        self.width, self.height = width, height
        self.config = MissionConfig()
        self.prequal_config = PrequalConfig()
        self.scaleX = width * 0.7 / self.config.worldWidth
        self.scaleY = height * 0.8 / self.config.worldHeight
        
        self.subMass = self.config.subMass
        self.subInertia_Z = self.config.subInertia_Z
        self.subInertia_Y = self.config.subInertia_Y
        self.thrusterMaxForce = self.config.thrusterMaxForce
        self.netBuoyancyForce = (self.config.subVolume * self.config.waterDensity * self.config.gravity) - (self.subMass * self.config.gravity)
        
        self.current_commands = ThrusterCommands()
        self.resetSimulation()

    def cmd_callback(self, msg):
        """Maps ROS2 Twist (Brain) back to Thruster Commands (Body)."""
        self.current_commands.forward = msg.linear.x
        self.current_commands.lateral = msg.linear.y
        self.current_commands.vertical = msg.linear.z
        self.current_commands.yaw = msg.angular.z

    def resetSimulation(self):
        """Restores the world state and submarine position."""
        self.prequal_gate = PrequalGate(
            x = self.prequal_config.GATE_X_POS, center_y = self.config.worldHeight / 2,
            z_top = self.prequal_config.GATE_DEPTH_METERS, width = self.prequal_config.GATE_WIDTH_METERS,
            height = self.prequal_config.GATE_OPENING_HEIGHT, color = self.prequal_config.GATE_COLOR
        )
        self.subPhysics = SubmarinePhysicsState(
            x = self.prequal_config.START_X_POS, y = self.config.worldHeight / 2,
            z = self.prequal_config.START_Z_POS, heading = 0.0, pitch = 0.0
        )
        self.running = True

    def project3D(self, world_pos):
        dx = world_pos[0] - self.subPhysics.x
        dy = world_pos[1] - self.subPhysics.y
        dz = world_pos[2] - self.subPhysics.z  # Relative depth
        
        h = math.radians(-self.subPhysics.heading)
        p = math.radians(-self.subPhysics.pitch)
        ch, sh, cp, sp = math.cos(h), math.sin(h), math.cos(p), math.sin(p)
        
        x_yaw = dx * ch - dy * sh
        y_yaw = dx * sh + dy * ch
        
        # TRANSFORMATION FIX: 
        # Flip the signs here to ensure deeper objects (positive dz) 
        # result in a downward projection on the Y axis.
        cz = x_yaw * cp + dz * sp
        cy = -(x_yaw * sp - dz * cp)  # <--- Added negative sign to flip vertical
        cx = y_yaw
        
        if cz < 0.2: return None
            
        w, h_px = self.cameraSurface.get_size()
        f = w / (2 * math.tan(math.radians(self.config.cameraFov / 2)))
        
        # Screen Mapping (Screen Y: 0 is top, h_px is bottom)
        screen_x = int(w/2 - f * (cx/cz))
        screen_y = int(h_px/2 + f * (cy/cz))
        
        return screen_x, screen_y, math.hypot(dx, dy, dz)
    
    def generateCameraView(self):
        self.cameraSurface.fill(WATER_COLOR)
        w, h = self.cameraSurface.get_size()
        
        if self.prequal_gate:
            g = self.prequal_gate
            half_w = g.width / 2
            
            # Top Corners (1.5m)
            l_top = self.project3D((g.x, g.center_y - half_w, g.z_top))
            r_top = self.project3D((g.x, g.center_y + half_w, g.z_top))
            # Bottom Corners (3.0m - Deeper)
            l_bot = self.project3D((g.x, g.center_y - half_w, g.z_top + g.height))
            r_bot = self.project3D((g.x, g.center_y + half_w, g.z_top + g.height))

            if l_top and r_top:
                pygame.draw.line(self.cameraSurface, g.color, l_top[:2], r_top[:2], 6)
                if l_bot: pygame.draw.line(self.cameraSurface, g.color, l_top[:2], l_bot[:2], 6)
                if r_bot: pygame.draw.line(self.cameraSurface, g.color, r_top[:2], r_bot[:2], 6)

    def applyPhysics(self, dt, commands):
        """Calculates 4-DOF movement based on drag and thruster force."""
        f_surge = commands.forward * self.thrusterMaxForce
        f_sway = commands.lateral * self.thrusterMaxForce
        f_heave = commands.vertical * self.thrusterMaxForce
        
        # Simple Linear Accelerations
        ax = f_surge / self.subMass
        ay = f_sway / self.subMass
        az = (f_heave - self.netBuoyancyForce) / self.subMass
        
        self.subPhysics.velocity_x += ax * dt
        self.subPhysics.velocity_y += ay * dt
        self.subPhysics.velocity_z += az * dt
        
        self.subPhysics.x += self.subPhysics.velocity_x * dt
        self.subPhysics.y += self.subPhysics.velocity_y * dt
        self.subPhysics.z += self.subPhysics.velocity_z * dt
        self.subPhysics.heading = (self.subPhysics.heading + math.degrees(commands.yaw * dt)) % 360

    def render(self):
        """Draws the debugging dashboard on the Pi 5 display."""
        self.screen.fill(LIGHT_BLUE)
        # Top-down tracking
        sub_pos = (int(self.subPhysics.x * self.scaleX + 50), int(self.subPhysics.y * self.scaleY + 50))
        pygame.draw.circle(self.screen, YELLOW, sub_pos, 15)
        
        # Camera-in-picture
        scaled_cam = pygame.transform.scale(self.cameraSurface, (400, 300))
        self.screen.blit(scaled_cam, (self.width-420, 20))
        pygame.display.flip()

    def publish_data(self):
        """Sends simulated sensor readings to the AI."""
        # Depth
        depth_msg = Float32()
        depth_msg.data = float(self.subPhysics.z)
        self.depth_pub.publish(depth_msg)
        print(f"Published Depth {depth_msg}")

        # Image Conversion Pipeline
        img_data = pygame.surfarray.array3d(self.cameraSurface)
        img_data = img_data.swapaxes(0, 1)
        
        # FIX: Force the array to 8-bit integers before handing it to OpenCV
        import numpy as np # Make sure this is at the top of your file!
        img_data = img_data.astype(np.uint8) 
        
        img_bgr = cv2.cvtColor(img_data, cv2.COLOR_RGB2BGR)     
        
        # Build CompressedImage message manually
        msg = CompressedImage()
        msg.format = "jpeg"
        success, encoded_img = cv2.imencode('.jpg', img_bgr)
        
        if success:
            msg.data = encoded_img.tobytes()
            self.image_pub.publish(msg)
        else:
            print("WARNING: JPEG Compression Failed!") # Added to catch future errors

    def run(self):
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.cameraSurface = pygame.Surface((320, 240))
        self.clock = pygame.time.Clock()

        while self.running:
            rclpy.spin_once(self, timeout_sec=0.001)
            dt = self.clock.tick(60) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT: self.running = False

            self.generateCameraView() 
            self.publish_data()
            self.applyPhysics(dt, self.current_commands)
            self.render()


def main(args=None):
    rclpy.init(args=args)
    sim = SubmarineSimulator()
    try:
        sim.run()
    except KeyboardInterrupt:
        pass
    finally:
        pygame.quit()
        rclpy.shutdown
        
if __name__ == '__main__':
    main()