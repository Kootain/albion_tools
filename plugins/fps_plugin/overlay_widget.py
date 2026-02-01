from PySide6.QtWidgets import QLabel
from PySide6.QtCore import Qt, QTimer

class FPSOverlayWidget(QLabel):
    """FPS 显示组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignCenter)
        self.setWindowTitle("FPS")
        self.setText("-999.9 -999,9\nMapName_Placeholder")
        
        # 默认样式
        self.font_size = 24
        self.text_color = "#00FF00" # Green
        self.bg_color = "rgba(0, 0, 0, 100)"
        self.update_style()
        
        self.timer = QTimer(self)
        self.timer.start(1000) 

    def update_style(self):
        """应用样式"""
        self.setStyleSheet(f"""
            color: {self.text_color}; 
            font-size: {self.font_size}px; 
            font-weight: bold; 
            background-color: {self.bg_color}; 
            padding: 5px;
            border-radius: 5px;
            width: 50px;
        """)

    def set_config(self, font_size, text_color):
        """外部调用更新配置"""
        self.font_size = font_size
        self.text_color = text_color
        self.update_style()