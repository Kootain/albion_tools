from enum import IntEnum
from typing_extensions import CapsuleType
from pydantic import BaseModel, model_validator
from typing import Dict, Any, Union, Tuple
from PySide6.QtCore import Signal, QObject
from base.event_codes import EventCodes, EventType
import abc
from collections import defaultdict

event_parsers = defaultdict(lambda: defaultdict(lambda: None))

def event_parser(etype: EventType, code: int):
    def decorator(cls):
        if not event_parsers[etype][code]:
            cls.code = code
            cls.type = etype
            event_parsers[etype][code] = cls()

        else:
            if isinstance(event_parsers[etype][code], cls):
                return cls
            else:
                print(event_parsers[etype][code], cls, isinstance(event_parsers[etype][code], cls))
            raise ValueError(f"事件解析器 {etype} {code} 已注册")
        return cls
    return decorator

class GameEvent(BaseModel):
    code: int = 0
    type: EventType = 0
    raw_data: Dict[int, Any] = {}


class EventParserBase(abc.ABC):
    """
    游戏事件解析器基类
    所有游戏事件解析器类都必须继承自这个类并实现 parse 方法
    """
    code: int
    type: EventType
    debug: bool = False

    def parse(self, raw: GameEvent) -> GameEvent:
        event = self._parse(raw)
        event.code = self.code
        event.type = self.type
        event.raw_data = raw.raw_data
        return event

    @abc.abstractmethod
    def _parse(self, raw_data: GameEvent) -> GameEvent:
        """
        解析原始游戏事件数据
        
        Args:
            raw: 原始游戏事件数据
            
        Returns:
            解析后的 GameEvent 对象
        """
        pass


class RawPacketSignal(QObject):
    packet_received = Signal(object)

    def emit_packet(self, packet: object) -> None:
        """
        发射收到的数据包
        
        Args:
            packet: 要发射的数据包内容
        """
        self.packet_received.emit(packet)

    def _connect_signal(self, slot: callable) -> None:
        """
        连接信号到槽函数
        
        Args:
            slot: 要连接的槽函数
        """
        self.packet_received.connect(slot)

    def _disconnect_signal(self, slot: callable) -> None:
        """
        断开信号与槽函数的连接
        
        Args:
            slot: 要断开的槽函数
        """
        self.packet_received.disconnect(slot)




class PacketProvider(abc.ABC):

    def __init__(self, signal: RawPacketSignal):
        """
        初始化数据包提供者
        
        Args:
            signal: 用于传输数据包内容的信号
        """
        self.signal = signal

    def emit(self, packet: bytes) -> None:
        """
        发射收到的数据包
        
        Args:
            packet: 要发射的数据包内容
        """
        self.signal.emit_packet(packet)

    @abc.abstractmethod
    def start(self, signal: RawPacketSignal) -> bool:
        """
        启动网络抓包
        
        Args:
            signal: 用于传输数据包内容
        
        Returns:
            如果启动成功返回 True，否则返回 False
        """
        pass

    @abc.abstractmethod
    def stop(self) -> bool:
        """
        停止网络抓包
        
        Returns:
            如果停止成功返回 True，否则返回 False
        """
        pass

    def is_running(self) -> bool:
        """
        检查是否正在运行
        
        Returns:
            如果正在运行返回 True，否则返回 False
        """
        pass


class P(BaseModel):
    # 保留原有字段定义（默认值、类型校验）
    x: float = 0.0
    y: float = 0.0

    @model_validator(mode='before')
    @classmethod
    def validate_tuple_list_input(cls, values: Any) -> Union[dict, Any]:
        """
        Pydantic 前置验证器：将列表/元组转为字典格式，供模型初始化使用
        mode='before'：在字段校验前执行，处理原始输入
        """
        # 情况1：输入是列表/元组（长度必须为2）
        if isinstance(values, (list, tuple)):
            if len(values) != 2:
                raise ValueError(f"列表/元组必须包含2个元素（x,y），但收到 {len(values)} 个")
            # 转为字典格式（Pydantic 能识别的格式）
            return {"x": values[0], "y": values[1]}
        # 情况2：输入是字典/已实例化对象 → 直接返回（保留原有逻辑）
        return values

    def distance(self, other: 'P') -> float:
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5

    def model_dump(
        self,
        as_dict: bool = False,  # 新增参数：是否返回字典（兼容原有逻辑）
        **kwargs
    ) -> Union[tuple[float, float], dict[str, float]]:
        """
        重写model_dump方法，默认返回元组 (x,y)，可选返回字典
        :param as_dict: True=返回字典（原有行为），False=返回元组（自定义行为）
        :param kwargs: 透传父类model_dump的参数（如 exclude_none、include 等）
        :return: 元组或字典
        """
        # 先调用父类方法获取原始字典
        original_dict = super().model_dump(** kwargs)
        
        # 根据as_dict参数返回对应格式
        if as_dict:
            return original_dict
        return (original_dict["x"], original_dict["y"])

class ObjectType(IntEnum):
    Unknown = 0
    Player = 1
    Mob = 2


class ObjectSubType(IntEnum):
    Unknown = 0
    LocalPlayer = 1
    Player = 2
    PvpPlayer = 3
    Mob = 4
    Boss = 5


class SlotType(IntEnum):
    MainHand = 0
    OffHand = 1
    Head = 2
    Chest = 3
    Shoes = 4
    Bag = 5
    Cape = 6
    Mount = 7
    Potion = 8
    BuffFood = 9


class Item(BaseModel):
    slot_type: SlotType
    index: int
    spells: list[int] = []

class SlotSpell(BaseModel):
    slot_type: SlotType
    value: int

class Equipment(BaseModel):
    main_hand: Item = Item(slot_type=SlotType.MainHand, index=0)
    off_hand: Item = Item(slot_type=SlotType.OffHand, index=0)
    head: Item = Item(slot_type=SlotType.Head, index=0)
    chest: Item = Item(slot_type=SlotType.Chest, index=0)
    shoes: Item = Item(slot_type=SlotType.Shoes, index=0)
    bag: Item = Item(slot_type=SlotType.Bag, index=0)
    cape: Item = Item(slot_type=SlotType.Cape, index=0)
    mount: Item = Item(slot_type=SlotType.Mount, index=0)
    potion: Item = Item(slot_type=SlotType.Potion, index=0)
    buff_food: Item = Item(slot_type=SlotType.BuffFood, index=0)

class Entity(BaseModel):
    oid: int
    user_guid: int = 0
    name: str
    guild: str
    equipment: Equipment
    otype: ObjectType 
    osub_type: ObjectSubType


