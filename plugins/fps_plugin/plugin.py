"""
FPS 插件主类
整合 overlay 和 config 组件
"""
from core.events.response.join import JoinFinishResponseEvent
from core.events.response.change_cluster import ChangeClusterResponseEvent
from core.events.request.move import MoveRequestEvent
from base.plugin import BasePlugin
from base.event_codes import EventType
from .overlay_widget import FPSOverlayWidget
from .config_widget import FPSConfigWidget
from base.base2 import P


class FPSPlugin(BasePlugin):
    """FPS 监控插件"""
    
    def __init__(self):
        super().__init__("fps_plugin", "FPS Monitor",)
        
        self._overlay_widget = None
        self._config_widget = None
        self.pos = P(x=-999.9, y=-999.9)
        self.map_name = "Mapname_Placeholder"
        
        # 设置默认配置（如果配置不存在）
        if not self.get_config("font_size"):
            self.set_config("font_size", 24)
        if not self.get_config("text_color"):
            self.set_config("text_color", "#00FF00")
            
        # 默认显示
        if self.get_config("visible") is None:
            self.set_config("visible", True)

    def get_overlay_widget(self):
        if not self._overlay_widget:
            self._overlay_widget = FPSOverlayWidget()
            # 应用配置
            self._overlay_widget.set_config(
                self.get_config("font_size", 24),
                self.get_config("text_color", "#00FF00")
            )
            self._overlay_widget.setVisible(self.get_config("visible", True))
        return self._overlay_widget

    def get_config_widget(self):
        if not self._config_widget:
            # 传递当前配置
            config_dict = {
                "font_size": self.get_config("font_size", 12),
                "text_color": self.get_config("text_color", "#00FF00")
            }
            self._config_widget = FPSConfigWidget(config_dict)
            self._config_widget.config_changed.connect(self._on_config_changed)
        return self._config_widget

    def _on_config_changed(self, font_size, text_color):
        """处理配置变更"""
        # 更新配置
        self.set_config("font_size", font_size)
        self.set_config("text_color", text_color)
        
        # 实时更新 Overlay
        if self._overlay_widget:
            self._overlay_widget.set_config(font_size, text_color)

    def handle_event(self, event):
        if isinstance(event, MoveRequestEvent):
            self.pos = P(x=round(event.pos.x, 1), y=round(event.pos.y, 1))
        if isinstance(event, ChangeClusterResponseEvent):
            self.map_name = event.cluster_name
        if isinstance(event, JoinFinishResponseEvent):
            self.pos = P(x=round(event.new_pos.x, 1), y=round(event.new_pos.y, 1))
        self._overlay_widget.setText(f"{self.pos.x} {self.pos.y}\n{self.map_name}")
