import math

# --- Colors (RGB) ---
WHITE = (255, 255, 255); BLACK = (0, 0, 0); GRAY = (100, 100, 100)
RED = (200, 0, 0); GREEN = (0, 200, 0); BLUE = (0, 0, 200)
YELLOW = (255, 255, 0); ORANGE = (255, 165, 0); LIGHT_BLUE = (173, 216, 230)
WATER_COLOR = (0, 100, 150); POOL_FLOOR_COLOR = (0, 80, 120); CONTROL_BOX_GRAY = (60, 60, 60)

class MissionConfig:
    def __init__(self):
        # --- World Dimensions ---
        self.worldWidth = 20.0
        self.worldHeight = 20.0
        self.worldDepth = 5.0
        
        # --- Physics Constants (Required by Simulator.py) ---
        self.gravity = 9.81
        self.waterDensity = 1000.0
        self.subMass = 15.0
        self.subVolume = 0.0152     
        self.submarineLength = 0.5
        self.submarineWidth = 0.3
        
        # Inertia (The specific line that crashed)
        self.subInertia_Z = 0.5     # Yaw inertia
        self.subInertia_Y = 0.5     # Pitch inertia
        
        self.thrusterMaxForce = 20.0 
        
        # Drag Coefficients
        self.surgeDragCoeff = 15.0
        self.swayDragCoeff = 25.0
        self.heaveDragCoeff = 30.0
        self.angularDragCoeff_Z = 5.0
        self.angularDragCoeff_Y = 5.0
        
        # Camera Settings
        self.cameraFov = 90.0       

        # --- Vision HSV Ranges (Required by AI) ---
        self.red_hsv_ranges = [((0, 100, 100), (10, 255, 255)), ((160, 100, 100), (180, 255, 255))]
        self.orange_hsv_ranges = [((10, 100, 100), (25, 255, 255))]
        self.green_hsv_range = [((40, 100, 100), (80, 255, 255))]
        
        # --- AI Vision Thresholds (Required by Submarine.py) ---
        self.min_gate_pixels = 200     
        self.min_marker_pixels = 100   
        self.min_pole_pixels = 100     
        self.target_gate_width = 150   
        
        # --- Control Gains ---
        self.depth_p_gain = 0.8         
        self.depth_tolerance = 0.1

class PrequalConfig:
    def __init__(self):
        self.START_X_POS = 1.0
        self.START_Z_POS = 0.5      
        self.GATE_X_POS = 8.0
        self.GATE_DEPTH_METERS = 1.5
        self.GATE_WIDTH_METERS = 3.0
        self.GATE_OPENING_HEIGHT = 1.5
        self.GATE_COLOR = RED
        self.MARKER_X_POS = 15.0
        self.MARKER_DIAMETER_METERS = 0.2
        self.POLE_ABOVE_SURFACE_METERS = 0.5
        self.MARKER_COLOR = ORANGE

# Create the instances that the other scripts import
config = MissionConfig()
prequal_config = PrequalConfig()