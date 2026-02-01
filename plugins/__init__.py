"""
Plugins 包
提供所有UI插件
"""
from PySide6.QtCore import QPoint
from .fps_plugin.plugin import FPSPlugin
from .log_plugin.plugin import LogPlugin
from .player_detector.plugin import PlayerPlugin
from .autodrive_plugin.path_recorder import PathRecorderPlugin


log_plugin = LogPlugin()
player_plugin = PlayerPlugin()
fps_plugin = FPSPlugin()
path_recorder_plugin = PathRecorderPlugin()

def register_default_plugins(overlay, dashboard, vision_manager=None):
    """
    注册所有默认插件到 Overlay 和 Dashboard
    
    Args:
        overlay: MasterOverlay 实例
        dashboard: ControlDashboard 实例
        vision_manager: VisionManager 实例
    """
    # 创建插件列表
    plugins = [
        fps_plugin,
        log_plugin,
        player_plugin,
        path_recorder_plugin
        # TODO: 添加更多插件
        # NetworkStatsPlugin(event_bus),
        # MapPlugin(event_bus),
    ]

    # for plugin in plugins:
        # network_manager.register_plugin(plugin)
    
    for plugin in plugins:
        # 注入 VisionManager
        if vision_manager:
            plugin.vision_manager = vision_manager
            
        dashboard.register_plugin(plugin)
        plugin.on_load()
        
        # 从配置恢复 Overlay 位置
        config = plugin.config
        if config.overlay_position:
            pos = QPoint(*config.overlay_position)
        else:
            pos = QPoint(50, 50)
        
        # 注册到 Overlay (添加显示组件)
        overlay.register_plugin(plugin, initial_pos=pos)
    
    print(f"[Plugins] 已注册 {len(plugins)} 个插件")


__all__ = ['FPSPlugin', 'LogPlugin', 'register_default_plugins']
