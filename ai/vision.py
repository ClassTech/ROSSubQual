import cv2
import numpy as np

def find_blobs_hsv(hsv_img, hsv_ranges, min_pixels):
    """
    Filters an HSV image by color ranges and identifies distinct objects (blobs).
    
    Args:
        hsv_img (numpy.ndarray): The source image in HSV color space.
        hsv_ranges (list): A list of tuples [((h_min, s_min, v_min), (h_max, s_max, v_max))].
        min_pixels (int): The minimum contour area to be considered a valid blob.
        
    Returns:
        list: A list of dictionaries, each containing 'x', 'y', 'width', 'height', and 'area'.
        numpy.ndarray: The final binary mask used for detection (useful for debugging).
    """
    # Initialize an empty black mask the same size as the input image
    mask = np.zeros(hsv_img.shape[:2], dtype="uint8")
    
    # Red often requires two ranges (e.g., 0-10 and 170-180). 
    # This loop combines all provided ranges into a single binary mask.
    for (lower_tuple, upper_tuple) in hsv_ranges:
        # Convert tuples to NumPy arrays for OpenCV C++ compatibility
        lower_np = np.array(lower_tuple, dtype="uint8")
        upper_np = np.array(upper_tuple, dtype="uint8")
        
        # Create a mask for the current range and merge it with the global mask
        curr_mask = cv2.inRange(hsv_img, lower_np, upper_np)
        mask = cv2.bitwise_or(mask, curr_mask)
    
    # Clean up the mask: remove small noise and close gaps in the detection
    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    
    # Identify the outer boundaries of the colored shapes
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    blobs = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        
        # Filter out objects that are too small to be the target
        if area > min_pixels:
            x, y, w, h = cv2.boundingRect(cnt)
            
            # Map coordinates to the dictionary format expected by data_structures.py
            blobs.append({
                'x': int(x),
                'y': int(y),
                'width': int(w),   # Required for pole/gate identification logic
                'height': int(h),  # Required for pole/gate identification logic
                'area': float(area)
            })
            
    # Return both the data and the mask so the simulator can display the 'vision' view
    return blobs, mask