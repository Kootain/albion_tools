from PySide6.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QPushButton, QLabel, QHBoxLayout, QFormLayout, QComboBox, QCheckBox
from PySide6.QtCore import Signal, Qt

from core.config.storage import global_config_manager

class GeneralSettingsPanel(QWidget):
    """
    通用设置面板
    包含全局性的设置，如蒙层编辑模式开关、语言、主题等。
    """
    # 信号：请求切换蒙层编辑模式
    toggle_overlay_edit_mode = Signal()
    # 信号: FPS显示开关
    show_fps_changed = Signal(bool)
    # 信号: 抓包模式变更
    sniffer_mode_changed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # --- 1. 蒙层控制 ---
        overlay_group = QGroupBox("蒙层控制 (Overlay Control)")
        overlay_layout = QVBoxLayout(overlay_group)
        
        # 状态说明
        self.status_label = QLabel("当前模式: 锁定 (F2 可编辑)")
        self.status_label.setStyleSheet("color: #888888; font-style: italic;")
        
        # 切换按钮
        self.toggle_button = QPushButton("启用 UI 编辑模式")
        self.toggle_button.setCursor(Qt.PointingHandCursor)
        self.toggle_button.setFixedHeight(40)
        self.toggle_button.clicked.connect(self._handle_toggle_click)
        
        overlay_layout.addWidget(self.status_label)
        overlay_layout.addWidget(self.toggle_button)
        layout.addWidget(overlay_group)

        # --- 2. 抓包设置 (Sniffer Settings) ---
        sniffer_group = QGroupBox("抓包设置 (Sniffer)")
        sniffer_layout = QFormLayout(sniffer_group)
        
        self.sniffer_mode_combo = QComboBox()
        self.sniffer_mode_combo.addItems(["本地抓包 (Local Libpcap)", "远程/Go转发 (Remote UDP)"])
        # Load initial value
        current_mode = global_config_manager.get_setting("general", "sniffer_mode", "local")
        self.sniffer_mode_combo.setCurrentIndex(1 if current_mode == "remote" else 0)
        self.sniffer_mode_combo.currentIndexChanged.connect(self._on_sniffer_mode_changed)
        
        sniffer_layout.addRow("抓包模式:", self.sniffer_mode_combo)
        layout.addWidget(sniffer_group)

        # --- 3. 插件开关 (Plugin Toggles) ---
        plugins_group = QGroupBox("插件开关 (Plugins)")
        plugins_layout = QVBoxLayout(plugins_group)
        
        self.fps_check = QCheckBox("显示 FPS 监控 (Show FPS Overlay)")
        self.fps_check.setChecked(True) # 默认选中，实际会由 Dashboard 同步
        self.fps_check.toggled.connect(self.show_fps_changed.emit)
        plugins_layout.addWidget(self.fps_check)
        
        layout.addWidget(plugins_group)

        # --- 3. 外观设置 (示例) ---
        appearance_group = QGroupBox("外观设置 (Appearance)")
        form_layout = QFormLayout(appearance_group)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["深色模式 (Dark)", "浅色模式 (Light)"])
        form_layout.addRow("界面主题:", self.theme_combo)
        
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["简体中文", "English"])
        form_layout.addRow("语言:", self.lang_combo)
        
        layout.addWidget(appearance_group)

        # 弹簧，把内容顶上去
        layout.addStretch()

    def _on_sniffer_mode_changed(self, index: int):
        mode = "remote" if index == 1 else "local"
        global_config_manager.set_setting("general", "sniffer_mode", mode)
        self.sniffer_mode_changed.emit(mode)
        
    def set_fps_visible(self, visible: bool):
        """外部设置 FPS 开关状态"""
        self.fps_check.blockSignals(True)
        self.fps_check.setChecked(visible)
        self.fps_check.blockSignals(False)

    def _handle_toggle_click(self):
        """处理按钮点击，发出信号"""
        self.toggle_overlay_edit_mode.emit()

    def update_mode_ui(self, is_editing: bool):
        """更新 UI 状态"""
        if is_editing:
            self.status_label.setText("当前模式: 编辑中 (UI 可拖拽)")
            self.status_label.setStyleSheet("color: #00A3DA; font-weight: bold;")
            self.toggle_button.setText("锁定 UI 并返回游戏")
            self.toggle_button.setStyleSheet("background-color: #d32f2f; color: white;") # 红色警示
        else:
            self.status_label.setText("当前模式: 锁定 (F2 可编辑)")
            self.status_label.setStyleSheet("color: #888888; font-style: italic;")
            self.toggle_button.setText("启用 UI 编辑模式")
            self.toggle_button.setStyleSheet("") # 恢复默认
