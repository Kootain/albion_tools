"""
插件基类
所有插件必须继承此类
"""
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import QObject
from typing import Any, Optional
from base.base2 import GameEvent
from core.config import global_config_manager, PluginConfig


class BasePlugin:
    """
    所有插件必须继承的基类
    
    提供：
    - 配置管理（自动加载/保存）
    - 事件处理接口
    - UI 组件接口
    """
    
    def __init__(self, plugin_id: str, display_name: str):
        self.id = plugin_id
        self._display_name = display_name
        
        # 加载配置
        self.config_manager = global_config_manager
        self.config = self.config_manager.load_plugin_config(plugin_id)
        
        self.vision_manager = None
    
    @property
    def display_name(self) -> str:
        """插件在 UI 上显示的名称"""
        return self._display_name
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """
        获取配置项
        
        Args:
            key: 配置键
            default: 默认值
            
        Returns:
            配置值
        """
        return self.config.custom_settings.get(key, default)
    
    def set_config(self, key: str, value: Any) -> bool:
        """
        设置配置项并自动保存
        
        Args:
            key: 配置键
            value: 配置值
            
        Returns:
            保存是否成功
        """
        self.config.custom_settings[key] = value
        return self.config_manager.save_plugin_config(self.id, self.config)
    
    def update_overlay_position(self, x: int, y: int) -> bool:
        """
        更新 Overlay 位置
        
        Args:
            x: X 坐标
            y: Y 坐标
            
        Returns:
            保存是否成功
        """
        return self.config_manager.update_overlay_position(self.id, (x, y))
    
    def update_overlay_opacity(self, opacity: float) -> bool:
        """
        更新 Overlay 透明度
        
        Args:
            opacity: 透明度 (0.0-1.0)
            
        Returns:
            保存是否成功
        """
        return self.config_manager.update_overlay_opacity(self.id, opacity)
    
    def set_overlay_visible(self, visible: bool):
        """
        设置 Overlay 可见性
        
        Args:
            visible: 是否可见
        """
        self.set_config("visible", visible)
        widget = self.get_overlay_widget()
        if widget:
            widget.setVisible(visible)

    def get_overlay_visible(self) -> bool:
        """
        获取 Overlay 可见性
        
        Returns:
            是否可见
        """
        return self.get_config("visible", True)

    def on_load(self):
        """插件加载时执行的初始化操作"""
        pass
    
    def get_overlay_widget(self) -> Optional[QWidget]:
        """返回要在蒙层上显示的 UI 组件"""
        return None
    
    def get_config_widget(self) -> Optional[QWidget]:
        """返回在控制面板上显示的配置 UI 组件"""
        return None
    
    def handle_event(self, event: GameEvent):
        """处理订阅到的游戏事件"""
        pass
    
    def save_config(self) -> bool:
        """
        保存当前配置
        
        Returns:
            保存是否成功
        """
        return self.config_manager.save_plugin_config(self.id, self.config)