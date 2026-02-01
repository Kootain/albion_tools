from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel, QApplication
from PySide6.QtCore import Qt, QSize

class CustomTitleBar(QWidget):
    """
    自定义 Mac 风格标题栏
    包含红黄绿三个控制按钮和标题文本。
    """
    def __init__(self, parent=None, title=""):
        super().__init__(parent)
        self.setFixedHeight(30)
        self.parent_window = parent
        self._setup_ui(title)
        
        # 拖拽相关变量
        self._is_dragging = False
        self._drag_position = None

    def _setup_ui(self, title):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setSpacing(8)

        # --- 1. 交通灯按钮 (Traffic Lights) ---
        self.btn_close = self._create_circle_btn("#ff5f56", "#e0443e") # Red
        self.btn_minimize = self._create_circle_btn("#ffbd2e", "#dea123") # Yellow
        self.btn_maximize = self._create_circle_btn("#27c93f", "#1aab29") # Green

        self.btn_close.clicked.connect(self._on_close_clicked)
        self.btn_minimize.clicked.connect(self._on_minimize_clicked)
        self.btn_maximize.clicked.connect(self._on_maximize_clicked)

        layout.addWidget(self.btn_close)
        layout.addWidget(self.btn_minimize)
        layout.addWidget(self.btn_maximize)

        # --- 2. 标题 ---
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("color: #cccccc; font-weight: bold; font-family: 'Segoe UI';")
        self.title_label.setAlignment(Qt.AlignCenter)
        
        layout.addStretch()
        layout.addWidget(self.title_label)
        layout.addStretch() # 居中标题

    def _create_circle_btn(self, color, hover_color):
        btn = QPushButton()
        btn.setFixedSize(12, 12)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                border-radius: 6px;
                border: none;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
        """)
        return btn

    # --- 窗口控制槽函数 ---
    def _on_close_clicked(self):
        if self.parent_window:
            self.parent_window.close()

    def _on_minimize_clicked(self):
        if self.parent_window:
            self.parent_window.showMinimized()

    def _on_maximize_clicked(self):
        if self.parent_window:
            if self.parent_window.isMaximized():
                self.parent_window.showNormal()
            else:
                self.parent_window.showMaximized()

    # --- 拖拽逻辑 ---
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._is_dragging = True
            self._drag_position = event.globalPos() - self.parent_window.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self._is_dragging and event.buttons() == Qt.LeftButton:
            self.parent_window.move(event.globalPos() - self._drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._is_dragging = False
