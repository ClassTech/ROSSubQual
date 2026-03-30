import numpy as np

class ThrusterCommands:
    """Standardized 6-DOF thruster output container (-1.0 to 1.0)."""
    def __init__(self, forward=0.0, lateral=0.0, vertical=0.0, yaw=0.0):
        self.forward = np.clip(forward, -1.0, 1.0)
        self.lateral = np.clip(lateral, -1.0, 1.0)
        self.vertical = np.clip(vertical, -1.0, 1.0)
        self.yaw = np.clip(yaw, -1.0, 1.0)

    def __repr__(self):
        return f"Thruster(F:{self.forward:.2f}, L:{self.lateral:.2f}, V:{self.vertical:.2f}, Y:{self.yaw:.2f})"

class MPU6050Readings:
    """Container for IMU data from the Pi 5's sensors."""
    def __init__(self):
        self.ax = self.ay = self.az = self.gx = self.gy = self.gz = 0.0

class SensorSuite:
    """Unified input for the AI, accepting NumPy images and float sensor data."""
    def __init__(self, camera_image, x=0.0, y=0.0, depth=0.0, heading=0.0, pitch=0.0, imu=None):
        self.camera_image = camera_image # NumPy array (H, W, C)
        self.x, self.y, self.depth = x, y, depth
        self.heading, self.pitch = heading, pitch
        self.imu = imu if imu else MPU6050Readings()

    @property
    def camera_width(self):
        """Replaces surface.get_size()[0]"""
        return self.camera_image.shape[1] if self.camera_image is not None else 0

    @property
    def camera_height(self):
        """Replaces surface.get_size()[1]"""
        return self.camera_image.shape[0] if self.camera_image is not None else 0

class Vision:
    """Storage and logic for detected OpenCV blobs."""
    def __init__(self):
        self.red_blobs = []
        self.green_blobs = []

    def get_gate_pair(self):
        """Identifies two vertical red poles that form a gate."""
        poles = [b for b in self.red_blobs if b['height'] > b['width'] * 1.2]
        if len(poles) < 2: return None
        poles.sort(key=lambda p: p['center_x'])
        p1, p2 = poles[0], poles[1]
        # Verify vertical overlap to ensure they aren't noise
        y_overlap = min(p1['max_y'], p2['max_y']) - max(p1['min_y'], p2['min_y'])
        return (p1, p2) if y_overlap > 0 else None

    def is_gate_visible(self):
        return self.get_gate_pair() is not None