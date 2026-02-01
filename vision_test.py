import sys
import time
import threading
import numpy as np
from PySide6.QtCore import QCoreApplication, QTimer
from vision.game.manager import VisionManager
from vision.game.analyzer import BaseAnalyzer
from vision.core.capture import WindowCapture


# Mock Analyzer
class MockAnalyzer(BaseAnalyzer):
    def __init__(self):
        super().__init__("MockAnalyzer")
        self.process_count = 0

    def process(self, image):
        self.process_count += 1
        # Return dummy result
        return {"count": self.process_count}

def test_vision_module():
    # PySide6 的 Signal 必须依赖 QCoreApplication (或 QApplication) 的事件循环才能工作
    app = QCoreApplication(sys.argv)

    print("Initializing VisionManager...")
    
    manager = VisionManager(WindowCapture(window_title="Albion Online Client"), fps=10)
    
    analyzer = MockAnalyzer()
    manager.register_analyzer(analyzer)
    
    # Connect signal
    def on_result(name, data):
        print(f"Result from {name}: {data}")
    
    manager.analysis_result.connect(on_result)
    
    print("Starting VisionManager...")
    manager.start()
    
    # 使用 QTimer 在 2 秒后退出应用，替代 time.sleep
    def stop_test():
        print("Stopping VisionManager...")
        manager.stop()
        app.quit()

    QTimer.singleShot(2000, stop_test)
    
    # 启动事件循环
    print("Starting Event Loop...")
    app.exec()

if __name__ == "__main__":
    test_vision_module()
