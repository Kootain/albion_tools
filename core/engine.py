from re import T
from typing import Any, List
from collections import defaultdict
from PySide6.QtCore import Signal, QObject
import logging


from base import event_codes
from base.event_codes import EventCodes, EventType
from base.base2 import GameEvent, EventParserBase, RawPacketSignal
from network.manager import NetworkManager

from core.photon_parser import PhotonPacketParser
from core.events.game_event import parse
from core.events.game_event import register_event_parsers
import traceback

logger = logging.getLogger(__name__)


class GameEventDispatcher(QObject):
    game_event_received = Signal(object)

    def __init__(self) -> None:
        super().__init__()
        self._handlers = defaultdict[EventType, defaultdict[EventCodes, list]](lambda: defaultdict[EventCodes, list](list))
        self._debug_handlers: List[callable] = []
        register_event_parsers()

    def emit(self, event: GameEvent) -> None:
        """
        发射收到的游戏数据
        Args:
            event: 要发射的游戏数据内容
        """
        self.game_event_received.emit(event)
    
    def register(self, event_type: EventType, event_codes: List[EventCodes], handler: callable) -> None:
        """
        注册游戏事件处理函数
        
        Args:
            event_codes: 要注册的事件代码
            handler: 处理该事件的函数
        """
        if event_type == EventType.Debug:
            self._debug_handlers.append(handler)
        for event_code in event_codes or []:
            self._handlers[event_type][event_code].append(handler)

    def _dispatch(self, event: GameEvent) -> None:
        """
        分发游戏事件给所有注册的处理函数
        
        Args:
            event: 要分发的游戏事件
        """
        event = parse(event)

        for handler in self._handlers[event.type][event.code]:
            try:
                handler(event)
            except Exception as e:
                print(f"[GameEventDispatcher] 处理事件 {event.type} {event.code} 时出错: {e}")
                traceback.print_exc()
        for handler in self._debug_handlers:
            try:
                handler(event)
            except Exception as e:
                print(f"[GameEventDispatcher] debug 处理事件 {event.type} {event.code} 时出错: {e}")
                traceback.print_exc()



class Engine(object):
    def __init__(self):
        self.packet_signal = RawPacketSignal() # 原始数据包通道
        self.network_manager: PacketProvider = NetworkManager(target_ports=[5055, 5056, 5058]) # 网络管理器
        self.game_event_dispatcher = GameEventDispatcher() # 游戏事件分发器
        self.photon_parser = PhotonPacketParser(self.photon_handler) # Photon 协议解析器

    def photon_handler(self, event:GameEvent):
        if type(event) is dict:
            print(event)
        self.game_event_dispatcher._dispatch(event)
        
    def _worker(self, raw_packet: bytes) -> None:
        """
        工作线程, 接受原始网络层packet, photon解析, 游戏事件解析, 游戏事件分发
        """
        self.photon_parser.parse(raw_packet)

        
    def start(self) -> bool:
        """
        启动引擎
        
        Returns:
            如果启动成功返回 True，否则返回 False
        """
        self.network_manager.start(self.packet_signal)
        self.packet_signal._connect_signal(self._worker)
        return True


    def stop(self) -> bool:
        """
        停止引擎
        
        Returns:
            如果停止成功返回 True，否则返回 False
        """
        self.network_manager.stop()
        self.packet_signal._disconnect_signal(self._worker)
        return True