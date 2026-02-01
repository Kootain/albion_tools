"""
示例 Handler: 处理物品事件
演示如何处理特定类型的游戏事件
"""
from core.base.handler import EventHandler
from core.event_bus import GameEvent, PacketType


class ItemHandler(EventHandler):
    """
    物品事件处理器
    处理所有与物品相关的事件（获取、移动、删除等）
    """
    
    def __init__(self):
        super().__init__(priority=5)  # 中等优先级
        self.items_received = []
        self.items_moved = 0
        self.items_deleted = 0
    
    def can_handle(self, event: GameEvent) -> bool:
        """检查是否是物品相关事件"""
        return event.type in [
            PacketType.NEW_ITEM,
            PacketType.INVENTORY_MOVE,
            PacketType.INVENTORY_DELETE
        ]
    
    def handle(self, event: GameEvent) -> None:
        """处理物品事件"""
        if event.type == PacketType.NEW_ITEM:
            self._handle_new_item(event)
        elif event.type == PacketType.INVENTORY_MOVE:
            self._handle_item_move(event)
        elif event.type == PacketType.INVENTORY_DELETE:
            self._handle_item_delete(event)
    
    def _handle_new_item(self, event: GameEvent) -> None:
        """处理新物品事件"""
        item_data = event.payload.get("item", {})
        item_name = item_data.get("name", "Unknown")
        item_count = item_data.get("count", 1)
        
        self.items_received.append(item_name)
        print(f"[ItemHandler] 获得物品: {item_name} x{item_count}")
    
    def _handle_item_move(self, event: GameEvent) -> None:
        """处理物品移动事件"""
        self.items_moved += 1
        # print(f"[ItemHandler] 物品移动 (总计: {self.items_moved})")
    
    def _handle_item_delete(self, event: GameEvent) -> None:
        """处理物品删除事件"""
        self.items_deleted += 1
        print(f"[ItemHandler] 物品删除 (总计: {self.items_deleted})")
    
    def get_summary(self) -> dict:
        """获取物品处理摘要"""
        return {
            "items_received_count": len(self.items_received),
            "items_moved": self.items_moved,
            "items_deleted": self.items_deleted,
            "recent_items": self.items_received[-10:]  # 最近 10 个物品
        }
