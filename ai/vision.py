import cv2
import numpy as np

def find_blobs_hsv(camera_image, hsv_range, min_pixels):
    if camera_image is None or hsv_range is None:
        return []

    hsv = cv2.cvtColor(camera_image, cv2.COLOR_BGR2HSV)
    
    # Handle both [((min),(max))] and ((min),(max)) formats
    if isinstance(hsv_range, list) and len(hsv_range) == 1:
        actual_range = hsv_range[0]
    else:
        actual_range = hsv_range

    lower = np.array(actual_range[0], dtype="uint8")
    upper = np.array(actual_range[1], dtype="uint8")
    
    mask = cv2.inRange(hsv, lower, upper)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    blobs = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > min_pixels:
            x, y, w, h = cv2.boundingRect(cnt)
            M = cv2.moments(cnt)
            if M["m00"] != 0:
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                
                blobs.append({
                    'center_x': cX, 'center_y': cY,
                    'min_x': x, 'max_x': x + w,
                    'min_y': y, 'max_y': y + h,
                    'width': w, 'height': h, 'area': area
                })
    return blobs
