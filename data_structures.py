import numpy as np

class ThrusterCommands:
    def __init__(self, forward=0.0, lateral=0.0, vertical=0.0, yaw=0.0):
        self.forward = forward
        self.lateral = lateral
        self.vertical = vertical
        self.yaw = yaw

class MPU6050Readings:
    def __init__(self):
        self.ax = self.ay = self.az = self.gx = self.gy = self.gz = 0.0

class SensorSuite:
    def __init__(self, camera_image, x=0.0, y=0.0, depth=0.0, heading=0.0, pitch=0.0, imu=None):
        self.camera_image = camera_image 
        self.x, self.y, self.depth = x, y, depth
        self.heading, self.pitch = heading, pitch
        self.imu = imu if imu else MPU6050Readings()

    @property
    def camera_width(self):
        return self.camera_image.shape[1] if self.camera_image is not None else 0

class Vision:
    def __init__(self):
        self.red_blobs = []
        self.green_blobs = []

    def get_gate_pair(self):
        poles = [b for b in self.red_blobs if b['height'] > b['width'] * 1.5]
        if len(poles) < 2: return None
        poles.sort(key=lambda p: p['center_x'])
        p1, p2 = poles[0], poles[1]
        y_overlap = min(p1['max_y'], p2['max_y']) - max(p1['min_y'], p2['min_y'])
        return (p1, p2) if y_overlap > 0 else None

    def is_gate_visible(self):
        return self.get_gate_pair() is not None
