import numpy as np

class Sensors:  # Renamed from Sensors
    def __init__(self):
        self.camera = None
        self.depth = 0.0
        self.heading = 0.0
        self.pitch = 0.0
        self.roll = 0.0
        self.time = 0.0
        self.camera_width = 0
        self.camera_height = 0

class ThrusterCommands:
    def __init__(self, forward=0.0, lateral=0.0, vertical=0.0, yaw=0.0):
        self.forward = forward
        self.lateral = lateral
        self.vertical = vertical
        self.yaw = yaw

class Vision:
    def __init__(self):
        self.red_blobs = []
        self.orange_blobs = []
        self.green_blobs = []
        self.camera_frame = None

    def get_gate_pair(self):
        """
        Filters red blobs to find vertical poles.
        Uses the dictionary keys 'height' and 'width' from vision.py.
        """
        poles = [b for b in self.red_blobs if b['height'] > b['width'] * 1.2]
        
        if len(poles) < 2:
            return None
            
        # Sort by area to find the two most prominent poles
        poles.sort(key=lambda x: x['area'], reverse=True)
        return (poles[0], poles[1])