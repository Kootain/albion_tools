import threading
import time
import logging
from typing import List, Callable, Dict, Any
import numpy as np
from PySide6.QtCore import QObject, Signal

from vision.core.capture import BaseCapture, WindowCapture
from vision.game.analyzer import BaseAnalyzer

logger = logging.getLogger(__name__)

class VisionManager(QObject):
    # Signal to emit analysis results: (analyzer_name, result_data)
    analysis_result = Signal(str, dict)

    def __init__(self, capture_source: BaseCapture = None, fps: int = 10):
        super().__init__()
        self.capture_source = capture_source
        self.fps = fps
        self.analyzers: List[BaseAnalyzer] = []
        self._running = False
        self._thread = None
        self._lock = threading.Lock()

    def set_capture_source(self, capture_source: BaseCapture):
        with self._lock:
            self.capture_source = capture_source

    def register_analyzer(self, analyzer: BaseAnalyzer):
        with self._lock:
            self.analyzers.append(analyzer)
            logger.info(f"Registered analyzer: {analyzer.name}")

    def remove_analyzer(self, analyzer_name: str):
        with self._lock:
            self.analyzers = [a for a in self.analyzers if a.name != analyzer_name]

    def start(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()
        logger.info("VisionManager started")

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=2.0)
        logger.info("VisionManager stopped")

    def _loop(self):
        interval = 1.0 / self.fps
        while self._running:
            start_time = time.time()
            
            if self.capture_source:
                image = self.capture_source.capture()
                if image is not None:
                    self._process_image(image)
            
            elapsed = time.time() - start_time
            sleep_time = max(0, interval - elapsed)
            time.sleep(sleep_time)

    def _process_image(self, image: np.ndarray):
        with self._lock:
            current_analyzers = list(self.analyzers)
        
        for analyzer in current_analyzers:
            try:
                result = analyzer.process(image)
                if result:
                    self.analysis_result.emit(analyzer.name, result)
            except Exception as e:
                logger.error(f"Error in analyzer {analyzer.name}: {e}")
