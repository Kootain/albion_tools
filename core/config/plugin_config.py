"""
插件配置数据模型
"""
from dataclasses import dataclass, field
from typing import Optional, Tuple, Dict, Any


@dataclass
class PluginConfig:
    """
    插件配置数据类
    
    包含插件的所有配置信息，包括：
    - 基础设置（启用状态）
    - UI 状态（位置、尺寸、透明度）
    - 自定义配置（插件特定的设置）
    """
    # 基础信息
    plugin_id: str
    enabled: bool = True
    
    # UI 状态
    overlay_position: Optional[Tuple[int, int]] = None
    overlay_size: Optional[Tuple[int, int]] = None
    overlay_opacity: float = 1.0
    
    # 插件特定配置
    custom_settings: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'PluginConfig':
        """从字典创建配置对象"""
        return cls(
            plugin_id=data.get('plugin_id', ''),
            enabled=data.get('enabled', True),
            overlay_position=tuple(data['overlay_position']) if data.get('overlay_position') else None,
            overlay_size=tuple(data['overlay_size']) if data.get('overlay_size') else None,
            overlay_opacity=data.get('overlay_opacity', 1.0),
            custom_settings=data.get('custom_settings', {})
        )
    
    def to_dict(self) -> dict:
        """转换为字典用于序列化"""
        return {
            'plugin_id': self.plugin_id,
            'enabled': self.enabled,
            'overlay_position': list(self.overlay_position) if self.overlay_position else None,
            'overlay_size': list(self.overlay_size) if self.overlay_size else None,
            'overlay_opacity': self.overlay_opacity,
            'custom_settings': self.custom_settings
        }
