"""
Handlers 包
提供所有业务逻辑处理器
"""
from .raw_data_handler import RawDataHandler
from .item_handler import ItemHandler


def register_default_handlers(network_manager):
    """
    注册所有默认的 Handlers 到 NetworkManager
    
    Args:
        network_manager: NetworkManager 实例
    """
    # 注册核心 Handlers
    network_manager.register_handler(RawDataHandler())
    network_manager.register_handler(ItemHandler())
    
    # TODO: 添加更多 Handlers
    # network_manager.register_handler(CombatHandler())
    # network_manager.register_handler(EconomyHandler())
    
    print(f"[Handlers] 已注册 {network_manager.get_handlers_info()['count']} 个 Handler")


__all__ = [
    'RawDataHandler',
    'ItemHandler',
    'register_default_handlers'
]
