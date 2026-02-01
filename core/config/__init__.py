"""
Core config package
配置管理系统
"""
from .plugin_config import PluginConfig
from .storage import ConfigManager, global_config_manager

__all__ = ['PluginConfig', 'ConfigManager', 'global_config_manager']
