import cv2
import numpy as np
from typing import Tuple, Optional, List

def resize_image(image: np.ndarray, scale: float) -> np.ndarray:
    """Resize image by a scale factor."""
    if image is None:
        return None
    width = int(image.shape[1] * scale)
    height = int(image.shape[0] * scale)
    return cv2.resize(image, (width, height), interpolation=cv2.INTER_AREA)

def crop_image(image: np.ndarray, x: int, y: int, w: int, h: int) -> np.ndarray:
    """Crop a region from the image."""
    if image is None:
        return None
    return image[y:y+h, x:x+w]

def match_template(image: np.ndarray, template: np.ndarray, threshold: float = 0.8) -> list[Tuple[int, int]]:
    """
    Find template in image.
    Returns list of (x, y) coordinates.
    """
    if image is None or template is None:
        return []
    
    result = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
    locations = np.where(result >= threshold)
    return list(zip(*locations[::-1]))

def filter_color(image: np.ndarray, lower: Tuple[int, int, int], upper: Tuple[int, int, int]) -> np.ndarray:
    """
    Filter image by HSV color range.
    Args:
        image: BGR image.
        lower: Lower HSV bound (h, s, v).
        upper: Upper HSV bound (h, s, v).
    Returns:
        Binary mask.
    """
    if image is None:
        return None
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, np.array(lower), np.array(upper))
    return mask

def find_contours(mask: np.ndarray) -> List[np.ndarray]:
    """Find contours in a binary mask."""
    if mask is None:
        return []
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return contours
