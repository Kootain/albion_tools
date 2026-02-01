from uuid import UUID
from base.base2 import EventParserBase, GameEvent, event_parser, P
from base.event_codes import EventCodes, EventType
from event_tool.object import object_to_guid
from game_data.world import get_map

class JoinFinishResponseEvent(GameEvent):
    timestamp: int
    guid: UUID
    username: str
    map_idx: str
    map_name: str
    new_pos: P

@event_parser(EventType.Response, 2)
class JoinFinishResponseEventParser(EventParserBase):

    def _parse(self, event: GameEvent) -> JoinFinishResponseEvent:
        timestamp = event.raw_data[0]
        guid = object_to_guid(event.raw_data[1])
        username = event.raw_data[2]
        new_pos = event.raw_data[9]
        map_idx = event.raw_data[65]
        map_data = get_map(map_idx)

        return JoinFinishResponseEvent(
            timestamp=timestamp,
            guid=guid,
            username=username,
            map_idx=map_idx,
            map_name=map_data.displayname,
            new_pos=P(x=new_pos[0], y=new_pos[1]),
        )