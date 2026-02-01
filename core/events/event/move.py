
import struct
from base.base2 import P, EventParserBase, GameEvent, event_parser
from base.event_codes import EventCodes, EventType

class MoveEvent(GameEvent):
    entity_id: int = 0
    time_ticks: int = 0
    pos: P = P(x=0.0, y=0.0)
    angle: int = 0
    speed: float = 0.0
    new_pos: P = P(x=0.0, y=0.0)

@event_parser(EventType.Event, EventCodes.Move)
class MoveEventParser(EventParserBase):

    def _parse(self, event: GameEvent) -> MoveEvent:
        params = event.raw_data or {}
        
        # OID is usually at key 0
        entity_id = params.get(0, 0)
        
        # Binary payload at key 1
        data = params.get(1)
        
        # Defaults
        time_ticks = 0
        x1, y1 = 0.0, 0.0
        x2, y2 = 0.0, 0.0
        angle = 0
        speed = 0.0
        
        if isinstance(data, (bytes, bytearray)) and len(data) >= 30:
            try:
                # Structure based on user confirmation that coords are floats
                # 0: B (Flag)
                # 1: Q (Timestamp)
                # 9: f (X1)
                # 13: f (Y1)
                # 17: B (Angle)
                # 18: f (Speed)
                # 22: f (X2)
                # 26: f (Y2)
                
                unpacked = struct.unpack('<B Q f f B f f f', data[:30])
                
                # flag = unpacked[0]
                time_ticks = unpacked[1]
                x1 = unpacked[2]
                y1 = unpacked[3]
                angle = unpacked[4]
                speed = unpacked[5]
                x2 = unpacked[6]
                y2 = unpacked[7]
                
            except struct.error:
                pass
        
        return MoveEvent(
            code=event.code,
            type=event.type,
            raw_data=params,
            entity_id=entity_id,
            time_ticks=time_ticks,
            pos=P(x=x1, y=y1),
            angle=angle,
            speed=speed,
            new_pos=P(x=x2, y=y2)
        )
