"""
示例 Handler: 处理原始数据包
用于演示 Handler 的基本使用
"""
from core.base.handler import EventHandler
from core.event_bus import GameEvent, PacketType


class RawDataHandler(EventHandler):
    """
    原始数据包处理器
    处理所有原始游戏数据事件，记录统计信息
    """
    
    def __init__(self):
        super().__init__(priority=0)  # 低优先级
        self.packet_count = 0
        self.total_bytes = 0
    
    def can_handle(self, event: GameEvent) -> bool:
        """检查是否是原始数据事件"""
        return event.type == PacketType.RAW_GAME_DATA
    
    def handle(self, event: GameEvent) -> None:
        """处理原始数据事件"""
        self.packet_count += 1
        data_len = event.payload.get("data_len", 0)
        self.total_bytes += data_len
        
        # 每 100 个数据包打印一次统计
        print(f"[RawDataHandler] 已处理 {self.packet_count} 个数据包，"
                f"总计 {self.total_bytes} 字节")
    
    def get_statistics(self) -> dict:
        """获取统计信息"""
        return {
            "packet_count": self.packet_count,
            "total_bytes": self.total_bytes,
            "average_size": self.total_bytes / self.packet_count if self.packet_count > 0 else 0
        }
