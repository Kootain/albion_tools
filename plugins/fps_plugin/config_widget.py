from PySide6.QtWidgets import QWidget, QFormLayout, QSpinBox, QComboBox, QGroupBox, QVBoxLayout
from PySide6.QtCore import Signal

class FPSConfigWidget(QWidget):
    """FPS 插件配置面板"""
    
    # 信号：配置发生变化 (font_size, color_hex)
    config_changed = Signal(int, str)

    def __init__(self, current_config: dict, parent=None):
        super().__init__(parent)
        self.config = current_config
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        group = QGroupBox("FPS 显示设置")
        form = QFormLayout(group)
        
        # 字体大小
        self.size_spin = QSpinBox()
        self.size_spin.setRange(10, 72)
        self.size_spin.setValue(self.config.get("font_size", 12))
        self.size_spin.valueChanged.connect(self._on_change)
        form.addRow("字体大小:", self.size_spin)
        
        # 颜色选择
        self.color_combo = QComboBox()
        self.colors = {
            "绿色 (Green)": "#00FF00",
            "红色 (Red)": "#FF0000",
            "黄色 (Yellow)": "#FFFF00",
            "白色 (White)": "#FFFFFF",
            "青色 (Cyan)": "#00FFFF"
        }
        for name, hex_code in self.colors.items():
            self.color_combo.addItem(name, hex_code)
        
        # 设置当前选中项
        current_color = self.config.get("text_color", "#00FF00")
        index = self.color_combo.findData(current_color)
        if index >= 0:
            self.color_combo.setCurrentIndex(index)
            
        self.color_combo.currentIndexChanged.connect(self._on_change)
        form.addRow("字体颜色:", self.color_combo)
        
        layout.addWidget(group)
        layout.addStretch()

    def _on_change(self):
        """当 UI 改变时发射信号"""
        font_size = self.size_spin.value()
        color_hex = self.color_combo.currentData()
        self.config_changed.emit(font_size, color_hex)
