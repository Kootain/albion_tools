from base.event_codes import EventType
from base.base2 import GameEvent
from photon_packet_parser import PhotonPacketParser as _PhotonPacketParser

def log(type, event_code, code):
    if type == "Response":
        print(f"{type} {event_code} {code}")

class PhotonPacketParser(object):
    def __init__(self, handler) -> None:
        self._parser = _PhotonPacketParser(self.on_event, self.on_request, self.on_response)
        self.handler = handler

    def _handle(self, event, code_idx):
        parameters = event.parameters
        code = event.parameters.get(code_idx, -1)
        return code, parameters

    def on_event(self, event) -> GameEvent:
        code, parameters = self._handle(event, 252)
        event_code = event.code
        # log("Event", event_code, code)
        if code == -1:
            # logger.warning(f"未找到 Response 事件代码 {event.parameters}")
            # return
            code = event_code
        self.handler(GameEvent(code=code, type=EventType.Event, raw_data=parameters))

    def on_request(self, event) -> GameEvent:
        code, parameters = self._handle(event, 253)
        event_code = event.operation_code
        # log("Request", event_code, code)
        if code == -1:
            # logger.warning(f"未找到 Request 事件代码 {event.parameters}")
            return
        self.handler(GameEvent(code=code, type=EventType.Request, raw_data=parameters))

    def on_response(self, event) -> GameEvent:
        code, parameters = self._handle(event, 253)
        event_code = event.operation_code
        # log("Response", event_code, code)
        if code == -1:
            # logger.warning(f"未找到 Response 事件代码 {event.parameters}")
            return
        self.handler(GameEvent(code=code, type=EventType.Response, raw_data=parameters))


    def parse(self, packet: bytes) -> GameEvent:
        self._parser.HandlePayload(packet)