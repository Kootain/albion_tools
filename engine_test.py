from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer  # 新增：用于唤醒Python解释器
from core.engine import Engine
import time
import sys
import signal  # 新增：处理系统信号

def handler(event):
    print(event)

def main():
    app = QApplication(sys.argv)
    
    # 1. 实例化引擎
    engine = Engine()
    engine.start()

    # 2. 定义SIGINT（Ctrl+C）处理函数：优雅退出
    def handle_interrupt(signum, frame):
        """处理Ctrl+C中断"""
        print("\n收到 KeyboardInterrupt，开始优雅退出...")
        # 停止引擎
        engine.stop()
        # 退出Qt事件循环
        app.quit()

    # 3. 注册SIGINT信号处理（跨平台）
    signal.signal(signal.SIGINT, handle_interrupt)

    # 4. 添加QTimer：定期触发空操作，让Python解释器响应信号
    # Qt事件循环会阻塞Python，定时器每100ms唤醒一次，确保SIGINT被处理
    timer = QTimer()
    timer.timeout.connect(lambda: None)  # 空操作
    timer.start(100)  # 每100ms触发一次

    # 5. 执行Qt事件循环，捕获KeyboardInterrupt（兜底）
    try:
        result = app.exec()
    except KeyboardInterrupt:
        print("\n捕获到 KeyboardInterrupt，强制退出...")
        engine.stop()
        result = 0  # 退出码
    
    # 6. 最终清理
    engine.stop()  # 确保引擎停止（双重保障）
    sys.exit(result)

if __name__ == "__main__":
    main()