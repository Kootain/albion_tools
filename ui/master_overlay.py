# ui/master_overlay.py

from PySide6.QtWidgets import QMainWindow, QWidget
from PySide6.QtCore import Qt, QTimer, QPoint, Signal
from ui.draggable_container import DraggableContainer
from ui import platform_utils

class MasterOverlay(QMainWindow):
    # 信号：通知 ControlDashboard 模式已更改
    edit_mode_changed = Signal(bool) 
    
    def __init__(self, target_window_title, parent=None):
        super().__init__(parent)
        
        self.target_title = target_window_title
        self.edit_mode = False 
        self.containers = {} # 存储所有 DraggableContainer 实例

        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("background-color: transparent;")

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.central_widget.setLayout(None) # 绝对布局

        self.show()
        QTimer.singleShot(100, lambda: self.set_click_through(True))
        
        self.follow_timer = QTimer(self)
        self.follow_timer.timeout.connect(self.update_overlay_position)
        self.follow_timer.start(500) 

    # --- 核心功能实现 ---
    
    def register_plugin(self, plugin, initial_pos=None):
        """注册插件到蒙层"""
        overlay_widget = plugin.get_overlay_widget()
        if overlay_widget:
            # 使用默认位置或指定位置
            pos = initial_pos if initial_pos else QPoint(100, 100)
            self.add_plugin_widget(plugin.id, overlay_widget, pos)

    def add_plugin_widget(self, plugin_id: str, content_widget: QWidget, initial_pos: QPoint):
        """接收插件 UI 并封装到可拖拽容器"""
        container = DraggableContainer(plugin_id, content_widget, parent=self.central_widget)
        
        # 连接位置保存信号
        container.position_changed.connect(self.handle_position_save)
        
        container.move(initial_pos)
        container.set_edit_mode(self.edit_mode)
        container.show()
        
        self.containers[plugin_id] = container

    def handle_position_save(self, plugin_id: str, new_pos: QPoint):
        # TODO: P3.1 阶段实现配置持久化
        print(f"[MasterOverlay] Saving position for {plugin_id}: {new_pos.x()}, {new_pos.y()}")

    def update_overlay_position(self):
        """窗体跟随逻辑 (P0.4)"""
        rect = platform_utils.get_target_window_rect(self.target_title)
        
        if rect:
            x, y, width, height = rect
            self.setGeometry(x, y, width, height)
            self.show()
        else:
            self.hide()
            
    def set_click_through(self, enable):
        """鼠标穿透逻辑 (支持 Windows 和 macOS)"""
        platform_utils.set_click_through(self, enable)
        
    def toggle_edit_mode(self):
        """切换编辑模式 (P2.5)"""
        self.edit_mode = not self.edit_mode
        self.set_click_through(not self.edit_mode)
        
        if self.edit_mode:
            self.setStyleSheet("background-color: rgba(0, 0, 0, 80);")
        else:
            self.setStyleSheet("background-color: transparent;")
            
        for container in self.containers.values():
            container.set_edit_mode(self.edit_mode)

        self.edit_mode_changed.emit(self.edit_mode)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_F2:
            self.toggle_edit_mode()
        super().keyPressEvent(event)