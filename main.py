# main.py

import sys
import time
from PySide6.QtWidgets import QApplication

# 核心框架
from core.engine import Engine
from base.base2 import EventType

# UI 层
from ui.master_overlay import MasterOverlay
from ui.control_dashboard import ControlDashboard

# 插件系统 (集中注册)
from plugins import register_default_plugins, log_plugin, player_plugin, path_recorder_plugin, fps_plugin

# TODO: 替换为你实际游戏窗口的精确标题
GAME_WINDOW_TITLE = "Albion Online Client" 
GAME_PORT = 5056  # Albion Online Photon 端口

def main():
    app = QApplication(sys.argv)

    # 1. 初始化核心 UI
    overlay = MasterOverlay(GAME_WINDOW_TITLE)
    dashboard = ControlDashboard()
    dashboard.show()
    

    # 2. 初始化游戏引擎
    engine = Engine()
    engine.start()
    engine.game_event_dispatcher.register(EventType.Debug, None, log_plugin.handle_event)
    engine.game_event_dispatcher.register(EventType.Debug, None, player_plugin.handle_event)
    engine.game_event_dispatcher.register(EventType.Debug, None, fps_plugin.handle_event)
    engine.game_event_dispatcher.register(EventType.Debug, None, path_recorder_plugin.handle_event)
   
    
    # 3. 注册插件（集中管理，自动恢复配置）
    register_default_plugins(overlay, dashboard)

    # 4. 连接信号槽 (逻辑核心)
    
    # A. 模式控制连接 (Dashboard <-> Overlay)
    dashboard.toggle_overlay_edit_mode.connect(overlay.toggle_edit_mode)
    
    # Overlay 状态变化 -> 更新 Dashboard UI
    def update_dashboard_ui(is_editing: bool):
        dashboard.update_mode_ui(is_editing)
        
    overlay.edit_mode_changed.connect(update_dashboard_ui)

    
    # 6. 运行应用
    result = app.exec()
    
    # 7. 清理
    engine.stop()
    sys.exit(result)

if __name__ == "__main__":
    main()
