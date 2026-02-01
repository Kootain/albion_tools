# ui/draggable_container.py

from PySide6.QtWidgets import QWidget, QVBoxLayout, QFrame
from PySide6.QtCore import Qt, QPoint, Signal, QObject

class DraggableContainer(QFrame):
    """
    可拖拽的容器，封装插件内容并提供编辑模式。
    """
    position_changed = Signal(str, QPoint) # 信号：通知保存新位置

    def __init__(self, plugin_id: str, content_widget: QWidget, parent: QWidget = None):
        super().__init__(parent)
        self.plugin_id = plugin_id
        self.is_editable = False    
        
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setObjectName("PluginContainer")
        self.setStyleSheet("""
            #PluginContainer { border: 1px solid transparent; border-radius: 5px; }
            #PluginContainer[editable="true"] {
                border: 2px dashed #00FF00; 
                background-color: rgba(0, 0, 0, 100); 
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5) 
        layout.addWidget(content_widget)
        self.adjustSize()

        self._dragging = False
        self._offset = QPoint()

    def set_edit_mode(self, editable: bool):
        self.is_editable = editable
        self.setProperty("editable", editable)
        self.style().polish(self)

    # --- 拖拽事件处理 ---
    def mousePressEvent(self, event):
        if self.is_editable and event.button() == Qt.LeftButton:
            self._dragging = True
            self._offset = event.position().toPoint()
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._dragging:
            new_pos = self.mapToParent(event.position().toPoint()) - self._offset
            self.move(new_pos)
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self._dragging:
            self._dragging = False
            # 拖拽结束，发出信号
            self.position_changed.emit(self.plugin_id, self.pos())
            event.accept()
        else:
            super().mouseReleaseEvent(event)