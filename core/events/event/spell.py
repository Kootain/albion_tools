from base.base2 import (
    EventParserBase,
    GameEvent,
    event_parser,
    Equipment,
    Entity,
    ObjectType,
    ObjectSubType,
    SlotType,
    SlotSpell,
)
from base.event_codes import EventCodes, EventType
from typing import List
from event_tool.object import to_int, to_str, to_int_list
from event_tool.equipment import parses_equipments


class CastStartEvent(GameEvent):
    oid: int
    spell_id: int


@event_parser(EventType.Event, 14)
class CastStartEventParser(EventParserBase):
    def _parse(self, event: GameEvent) -> CastStartEvent:
        params = event.raw_data or {}
        oid = params.get(0)
        spell_id = params.get(5)
        return CastStartEvent(oid=oid, spell_id=spell_id)