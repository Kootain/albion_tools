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


class NewCharacterEvent(GameEvent):
    entity: Entity




@event_parser(EventType.Event, 29)
class NewCharacterEventParser(EventParserBase):
    def _parse(self, event: GameEvent) -> NewCharacterEvent:
        params = event.raw_data or {}

        oid = to_int(params.get(0, 0))
        name = to_str(params.get(1, ""))
        user_guid = to_int(params.get(7, 0))
        guild_name = to_str(params.get(8, ""))

        equipment_values = to_int_list(params.get(40, []))
        spells = to_int_list(params.get(43, []))
        equipment = parses_equipments(equipment_values, spells)

        entity = Entity(
            oid=oid,
            user_guid=user_guid,
            name=name,
            guild=guild_name,
            equipment=equipment,
            otype=ObjectType.Player,
            osub_type=ObjectSubType.Player,
        )

        return NewCharacterEvent(entity=entity)
