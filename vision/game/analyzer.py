import abc
import numpy as np
from typing import Any, Dict

class BaseAnalyzer(abc.ABC):
    def __init__(self, name: str):
        self.name = name

    @abc.abstractmethod
    def process(self, image: np.ndarray) -> Dict[str, Any]:
        """
        Process the image and return extracted information.
        Args:
            image: The captured game image (BGR).
        Returns:
            Dict containing extracted data, or None/Empty dict if nothing found.
        """
        pass
