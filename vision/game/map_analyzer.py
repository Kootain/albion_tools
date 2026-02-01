import cv2
import numpy as np
from typing import Dict, Any, List, Tuple
from vision.game.analyzer import BaseAnalyzer
from vision.core.ocr import TextRecognizer
from vision.core.image_utils import crop_image, filter_color, find_contours

class MapAnalyzer(BaseAnalyzer):
    def __init__(self):
        super().__init__("MapAnalyzer")
        self.ocr = TextRecognizer()
        
        # HSV Color ranges for Yellow (Paths/Exits)
        # Adjust these based on actual game colors
        self.yellow_lower = (20, 100, 100)
        self.yellow_upper = (40, 255, 255)

    def process(self, image: np.ndarray) -> Dict[str, Any]:
        if image is None:
            return {}

        h, w = image.shape[:2]
        
        # 1. Extract Map Info (Top Left)
        # Approximate ROI: Top 10% height, Left 30% width
        # Based on screenshot: Top Bar is full width, but Name is Left, Hostile is Middle/Right
        
        # ROI 1: Name & Tier (Top Left)
        # e.g. x=0, y=0, w=25% W, h=10% H
        roi_name = crop_image(image, 0, 0, int(w * 0.25), int(h * 0.12))
        name_info = self._extract_text(roi_name)
        
        # ROI 2: Hostile Count (Top Middle-Left)
        # e.g. x=25% W, y=0, w=15% W, h=10% H
        roi_hostile = crop_image(image, int(w * 0.25), 0, int(w * 0.15), int(h * 0.12))
        hostile_info = self._extract_text(roi_hostile)

        # 2. Path Detection (Central Map Area)
        # The map is usually in the center. Let's look at the whole image for now or crop center.
        # Assuming the map is the diamond shape in the center.
        # For simplicity, we scan the whole image for yellow paths, 
        # but we might want to mask out the top bar UI.
        roi_map = crop_image(image, 0, int(h * 0.15), w, int(h * 0.85))
        paths, exits = self._detect_paths(roi_map)
        
        # Adjust coordinates back to full image
        offset_y = int(h * 0.15)
        exits = [(x, y + offset_y) for x, y in exits]
        # paths points adjustment omitted for brevity, but logic applies
        
        return {
            "name_tier": name_info,
            "hostile_info": hostile_info,
            "exits": exits,
            "path_count": len(paths)
        }

    def _extract_text(self, image: np.ndarray) -> List[str]:
        results = self.ocr.recognize(image)
        return [text for text, conf in results]

    def _detect_paths(self, image: np.ndarray) -> Tuple[List[np.ndarray], List[Tuple[int, int]]]:
        if image is None:
            return [], []
            
        mask = filter_color(image, self.yellow_lower, self.yellow_upper)
        contours = find_contours(mask)
        
        paths = []
        exits = []
        
        for cnt in contours:
            area = cv2.contourArea(cnt)
            # Filter noise
            if area < 50:
                continue
                
            # Distinguish Exits (Signposts) from Paths (Lines)
            # Exits are likely more "compact" or have specific shape
            # Paths are long and thin
            
            x, y, w, h = cv2.boundingRect(cnt)
            aspect_ratio = float(w) / h
            
            # Simple heuristic: 
            # Signposts might be somewhat square-ish or small blobs
            # Paths are very long
            
            # For now, let's just return centroids of all significant yellow blobs as "exits/nodes"
            M = cv2.moments(cnt)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                exits.append((cx, cy))
            
            paths.append(cnt)
            
        return paths, exits
