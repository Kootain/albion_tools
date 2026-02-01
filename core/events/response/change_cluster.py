from base.base2 import EventParserBase, GameEvent, event_parser
from base.event_codes import EventCodes, EventType
from game_data.world import get_map

class ChangeClusterResponseEvent(GameEvent):
    cluster_idx: str
    cluster_name: str

@event_parser(EventType.Response, 35)
class ChangeClusterResponseEventParser(EventParserBase):

    def _parse(self, event: GameEvent) -> ChangeClusterResponseEvent:
        raw_data = event.raw_data
        cluster_idx = str(raw_data[0])
        cluster_name = get_map(cluster_idx).displayname
        return ChangeClusterResponseEvent(cluster_idx=cluster_idx, cluster_name=cluster_name)