"""
配置存储管理器
负责插件配置的持久化
"""
import json
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from .plugin_config import PluginConfig


class ConfigManager:
    """
    配置存储管理器（单例模式）
    
    职责：
    - 加载和保存插件配置到 JSON 文件
    - 管理配置缓存
    - 提供便捷的配置读写 API
    """
    
    _instance: Optional['ConfigManager'] = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, config_dir: str = ".config"):
        # 避免重复初始化
        if hasattr(self, '_initialized'):
            return
        
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.configs: Dict[str, PluginConfig] = {}
        self._initialized = True
        
        print(f"[ConfigManager] 配置目录: {self.config_dir.absolute()}")
    
    def get_config_path(self, plugin_id: str) -> Path:
        """获取插件配置文件路径"""
        return self.config_dir / f"{plugin_id}.json"
    
    def load_plugin_config(self, plugin_id: str) -> PluginConfig:
        """
        加载插件配置
        
        Args:
            plugin_id: 插件 ID
            
        Returns:
            PluginConfig 对象（如果文件不存在则返回默认配置）
        """
        # 检查缓存
        if plugin_id in self.configs:
            return self.configs[plugin_id]
        
        config_path = self.get_config_path(plugin_id)
        
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    config = PluginConfig.from_dict(data)
                    self.configs[plugin_id] = config
                    print(f"[ConfigManager] 加载配置: {plugin_id}")
                    return config
            except Exception as e:
                print(f"[ConfigManager] 加载配置失败 {plugin_id}: {e}")
        
        # 返回默认配置
        config = PluginConfig(plugin_id=plugin_id)
        self.configs[plugin_id] = config
        return config
    
    def save_plugin_config(self, plugin_id: str, config: PluginConfig) -> bool:
        """
        保存插件配置
        
        Args:
            plugin_id: 插件 ID
            config: 配置对象
            
        Returns:
            保存是否成功
        """
        config_path = self.get_config_path(plugin_id)
        
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config.to_dict(), f, indent=2, ensure_ascii=False)
            
            self.configs[plugin_id] = config
            print(f"[ConfigManager] 保存配置: {plugin_id}")
            return True
        except Exception as e:
            print(f"[ConfigManager] 保存配置失败 {plugin_id}: {e}")
            return False
    
    def get_setting(self, plugin_id: str, key: str, default: Any = None) -> Any:
        """
        获取插件的特定配置项
        
        Args:
            plugin_id: 插件 ID
            key: 配置键
            default: 默认值
            
        Returns:
            配置值
        """
        config = self.load_plugin_config(plugin_id)
        return config.custom_settings.get(key, default)
    
    def set_setting(self, plugin_id: str, key: str, value: Any) -> bool:
        """
        设置插件的特定配置项
        
        Args:
            plugin_id: 插件 ID
            key: 配置键
            value: 配置值
            
        Returns:
            保存是否成功
        """
        config = self.load_plugin_config(plugin_id)
        config.custom_settings[key] = value
        return self.save_plugin_config(plugin_id, config)
    
    def update_overlay_position(self, plugin_id: str, position: Tuple[int, int]) -> bool:
        """
        更新插件 Overlay 位置
        
        Args:
            plugin_id: 插件 ID
            position: (x, y) 坐标
            
        Returns:
            保存是否成功
        """
        config = self.load_plugin_config(plugin_id)
        config.overlay_position = position
        return self.save_plugin_config(plugin_id, config)
    
    def update_overlay_opacity(self, plugin_id: str, opacity: float) -> bool:
        """
        更新插件 Overlay 透明度
        
        Args:
            plugin_id: 插件 ID
            opacity: 透明度 (0.0-1.0)
            
        Returns:
            保存是否成功
        """
        config = self.load_plugin_config(plugin_id)
        config.overlay_opacity = max(0.0, min(1.0, opacity))
        return self.save_plugin_config(plugin_id, config)


# 全局单例实例
global_config_manager = ConfigManager()
