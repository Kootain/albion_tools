from base.base2 import P, EventParserBase, GameEvent, event_parser
from base.event_codes import EventCodes, EventType

class MoveRequestEvent(GameEvent):
    timestamp: int
    pos: P
    direction: float
    speed: float

@event_parser(EventType.Request, 21)
class MoveRequestEventParser(EventParserBase):
    # debug = True

    def _parse(self, event: GameEvent) -> MoveRequestEvent:
        timestamp = event.raw_data[0]
        position = event.raw_data[1]
        direction = event.raw_data.get(2, 0)
        speed = event.raw_data.get(4, 0)
        return MoveRequestEvent(
            timestamp=timestamp,
            pos=P(x=position[0], y=position[1]),
            direction=direction,
            speed=speed,
        )