from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QListWidget, QStackedWidget, QListWidgetItem, QVBoxLayout
from PySide6.QtCore import Signal, QSize, Qt
from ui.panels.general_settings import GeneralSettingsPanel
from ui.components.custom_title_bar import CustomTitleBar

class ControlDashboard(QMainWindow):
    """
    游戏的配置和控制面板主窗口。
    采用自定义标题栏 + 侧边栏 + 内容区的现代布局。
    """
    # 信号：通知 MasterOverlay 切换模式 (转发自 GeneralSettingsPanel)
    toggle_overlay_edit_mode = Signal() 

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("游戏插件控制中心 (Albion Tools)")
        self.resize(900, 600)
        
        # 设置无边框窗口
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground) # 允许圆角透明
        
        # Resize related
        self._resize_margin = 8
        self._resize_drag_active = False
        self._resize_drag_position = None
        self.setMouseTracking(True)
        
        # 初始化 UI
        self._init_ui()
        self._apply_styles()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            position = self._get_resize_position(event.pos())
            if position:
                self._resize_drag_active = True
                self._resize_drag_position = position
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self._resize_drag_active = False
        self._resize_drag_position = None
        self.setCursor(Qt.ArrowCursor)
        super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        if self._resize_drag_active:
            self._handle_resize(event.globalPos())
        else:
            position = self._get_resize_position(event.pos())
            self._update_cursor(position)
        super().mouseMoveEvent(event)

    def _get_resize_position(self, pos):
        x = pos.x()
        y = pos.y()
        w = self.width()
        h = self.height()
        m = self._resize_margin

        on_left = x <= m
        on_right = x >= w - m
        on_top = y <= m
        on_bottom = y >= h - m

        if on_top and on_left:
            return "top_left"
        elif on_top and on_right:
            return "top_right"
        elif on_bottom and on_left:
            return "bottom_left"
        elif on_bottom and on_right:
            return "bottom_right"
        elif on_top:
            return "top"
        elif on_bottom:
            return "bottom"
        elif on_left:
            return "left"
        elif on_right:
            return "right"
        return None

    def _update_cursor(self, position):
        if position in ("top_left", "bottom_right"):
            self.setCursor(Qt.SizeFDiagCursor)
        elif position in ("top_right", "bottom_left"):
            self.setCursor(Qt.SizeBDiagCursor)
        elif position in ("top", "bottom"):
            self.setCursor(Qt.SizeVerCursor)
        elif position in ("left", "right"):
            self.setCursor(Qt.SizeHorCursor)
        else:
            self.setCursor(Qt.ArrowCursor)

    def _handle_resize(self, global_pos):
        if not self._resize_drag_position:
            return

        rect = self.geometry()
        x, y, w, h = rect.x(), rect.y(), rect.width(), rect.height()
        mx, my = global_pos.x(), global_pos.y()
        
        min_w, min_h = self.minimumSize().width(), self.minimumSize().height()
        min_w = max(min_w, 400) 
        min_h = max(min_h, 300)

        if "left" in self._resize_drag_position:
            new_w = x + w - mx
            if new_w >= min_w:
                x = mx
                w = new_w
        elif "right" in self._resize_drag_position:
            new_w = mx - x
            if new_w >= min_w:
                w = new_w
        
        if "top" in self._resize_drag_position:
            new_h = y + h - my
            if new_h >= min_h:
                y = my
                h = new_h
        elif "bottom" in self._resize_drag_position:
            new_h = my - y
            if new_h >= min_h:
                h = new_h

        self.setGeometry(x, y, w, h)

    def _init_ui(self):
        main_container = QWidget()
        main_container.setObjectName("MainContainer") 
        self.setCentralWidget(main_container)
        
        main_layout = QVBoxLayout(main_container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.title_bar = CustomTitleBar(self, title="Albion Tools Control Center")
        main_layout.addWidget(self.title_bar)

        content_container = QWidget()
        content_layout = QHBoxLayout(content_container)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(220)
        self.sidebar.setFrameShape(QListWidget.NoFrame)
        self.sidebar.currentRowChanged.connect(self._on_sidebar_change)
        content_layout.addWidget(self.sidebar)

        self.content_stack = QStackedWidget()
        content_layout.addWidget(self.content_stack)

        main_layout.addWidget(content_container)

        self._setup_panels()

    def _setup_panels(self):
        # Panel 1: 通用设置
        self.general_panel = GeneralSettingsPanel()
        self.general_panel.toggle_overlay_edit_mode.connect(self.toggle_overlay_edit_mode)
        self.general_panel.show_fps_changed.connect(self._on_fps_visibility_changed)
        self._add_nav_item("通用设置 (General)", "settings", self.general_panel)
        
        self.plugins = {} # id -> plugin instance

        # 默认选中第一项
        self.sidebar.setCurrentRow(0)

    def _on_fps_visibility_changed(self, visible: bool):
        if "fps_plugin" in self.plugins:
            self.plugins["fps_plugin"].set_overlay_visible(visible)

    def _add_nav_item(self, title: str, icon_name: str, widget: QWidget):
        """添加导航项和对应的页面"""
        item = QListWidgetItem(title)
        item.setSizeHint(QSize(0, 50)) # 设置行高
        item.setTextAlignment(0x0001 | 0x0080) # AlignLeft | AlignVCenter
        
        self.sidebar.addItem(item)
        self.content_stack.addWidget(widget)

    def _on_sidebar_change(self, index: int):
        """切换右侧页面"""
        self.content_stack.setCurrentIndex(index)

    def _apply_styles(self):
        """应用现代化 Dark Theme QSS"""
        self.setStyleSheet("""
            /* 主窗口背景和圆角 */
            #MainContainer {
                background-color: #202020;
                border-radius: 10px;
                border: 1px solid #333;
            }
            
            /* 标题栏背景 */
            CustomTitleBar {
                background-color: #252526;
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
                border-bottom: 1px solid #111;
            }

            /* 侧边栏样式 */
            QListWidget {
                background-color: #2b2b2b;
                color: #e0e0e0;
                outline: 0;
                border-bottom-left-radius: 10px;
            }
            QListWidget::item {
                padding-left: 15px;
                border-left: 3px solid transparent;
            }
            QListWidget::item:selected {
                background-color: #383838;
                color: #ffffff;
                border-left: 3px solid #00A3DA;
            }
            QListWidget::item:hover {
                background-color: #333333;
            }

            /* 通用组件样式 */
            QWidget {
                color: #e0e0e0;
                font-family: 'Segoe UI', sans-serif;
                font-size: 14px;
            }
            QGroupBox {
                border: 1px solid #444;
                border-radius: 5px;
                margin-top: 20px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px 0 3px;
            }
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 5px 15px;
            }
            QPushButton:hover {
                background-color: #0086f0;
            }
            QPushButton:pressed {
                background-color: #006cbd;
            }
            QComboBox {
                background-color: #333;
                color: #ffffff;
                border: 1px solid #555;
                border-radius: 3px;
                padding: 5px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #333;
                color: #ffffff;
                selection-background-color: #0078d4;
                selection-color: #ffffff;
            }
            QLineEdit, QSpinBox {
                background-color: #333;
                color: #ffffff;
                border: 1px solid #555;
                border-radius: 3px;
                padding: 5px;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                background-color: #444;
                border: none;
            }
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                background-color: #555;
            }
        """)

    def register_plugin(self, plugin):
        """注册插件到控制面板"""
        self.plugins[plugin.id] = plugin
        
        if plugin.id == "fps_plugin":
            # Sync initial state
            if hasattr(plugin, "get_overlay_visible"):
                self.general_panel.set_fps_visible(plugin.get_overlay_visible())

        config_widget = plugin.get_config_widget()
        if config_widget:
            self._add_nav_item(plugin.display_name, "plugin", config_widget)

    def update_mode_ui(self, is_editing: bool):
        """由 main.py 订阅 MasterOverlay 信号后调用，更新 UI"""
        self.general_panel.update_mode_ui(is_editing)
