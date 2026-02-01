import logging
import numpy as np
from typing import List, Tuple, Optional

logger = logging.getLogger(__name__)

try:
    from rapidocr_onnxruntime import RapidOCR
    _HAS_OCR = True
except ImportError:
    logger.warning("rapidocr-onnxruntime not found. OCR features will be disabled.")
    _HAS_OCR = False

class TextRecognizer:
    def __init__(self):
        self.ocr = None
        if _HAS_OCR:
            try:
                # det_use_gpu=False, cls_use_gpu=False, rec_use_gpu=False for compatibility
                self.ocr = RapidOCR(det_use_gpu=False, cls_use_gpu=False, rec_use_gpu=False)
            except Exception as e:
                logger.error(f"Failed to initialize RapidOCR: {e}")

    def recognize(self, image: np.ndarray) -> List[Tuple[str, float]]:
        """
        Recognize text in the image.
        Args:
            image: BGR numpy array.
        Returns:
            List of (text, confidence) tuples.
        """
        if not self.ocr or image is None:
            return []
        
        try:
            result, _ = self.ocr(image)
            if not result:
                return []
            
            # result format: [[[[x1, y1], [x2, y2], [x3, y3], [x4, y4]], text, confidence], ...]
            return [(line[1], line[2]) for line in result]
        except Exception as e:
            logger.error(f"OCR error: {e}")
            return []
