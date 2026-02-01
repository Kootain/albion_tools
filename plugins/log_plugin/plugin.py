 
from base.plugin import BasePlugin
from base.base2 import GameEvent
from ui.panels.log_panel import LogPanel
from core.events.event.move import MoveEvent
from game_data.items import get_item


class LogPlugin(BasePlugin):

    def __init__(self):
        super().__init__("log_plugin", "系统日志 (Logs)")
        self._config_widget = None


    def get_overlay_widget(self):
        return None

    def get_config_widget(self):
        if not self._config_widget:
            self._config_widget = LogPanel()
        return self._config_widget

    def handle_event(self, event: GameEvent):
        return
        if not self._config_widget:
            return

        if True:
            # ts = time.strftime('%H:%M:%S', time.localtime(event.timestamp))
            ts = "DEBUG"
            # if event.code == 3:
                # print(event)
            # if event.code == 90:
                # print(get_item(event.raw_data.get(2)[0]))
            msg = f"[{ts}] {event.type} {event.code}: {event.raw_data}"
            self._config_widget.append_event(event)
