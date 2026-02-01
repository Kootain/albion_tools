 
from typing import Any, Dict

from pydantic import BaseModel, Field
from base.plugin import BasePlugin
from base.base2 import GameEvent, P
from base.event_codes import EventCodes, EventType
from controllor.move import KeyboardController
import keyboard
from core.events.response.join import JoinFinishResponseEvent
from event_tool.object import object_to_guid
from core.events.request.move import MoveRequestEvent
from core.events.response.change_cluster import ChangeClusterResponseEvent 
from plugins.autodrive_plugin.path_compose import douglas_peucker
from collections import defaultdict
import time



class PathRecorderPlugin(BasePlugin):

    def __init__(self):
        super().__init__("path_recorder_plugin", "路径记录器 (Path Recorder)")
        self._config_widget = None
        self.status = 0 # 0: idle, 1: recording, 2: finished
        self.path_builder = None
        self.keyboard_controller = KeyboardController(duration_scale=0.05, rotation_angle=315)
        self.temp_path = None
        self.replay_status = 0 # 0: idle, 1: replaying
        self.pos = P(x=0, y=0)
        self.error_threshold = 1.
        self.path_compose_error_rate = 0.2
        self.map_path_data: MapPathData = MapPathData()
        self.current_map = None
        self._load_path_data()
        self.routine = {
            'Martlock -> Thetford': ['Haytor', 'Lewsdon Hill', 'Bonepool Marsh', 'Wispwhisper Marsh', 'Falsestep Marsh', 'Dusklight Fen', 'Thetford']
        }
        
        # Hotkey setup
        self.hotkey = self.get_config("hotkey", "F3")
        try:
            keyboard.add_hotkey(self.hotkey, self.toggle_record)
            keyboard.add_hotkey("F4", self.test)
        except Exception as e:
            print(f"Failed to register hotkey {self.hotkey}: {e}")

    def toggle_record(self):
        if self.status == 1:
            self.stop_record()
            print(f"[{self.display_name}] Recording Stopped")
        else:
            self.start_record() 
            print(f"[{self.display_name}] Recording Started")

    def _load_path_data(self):
        data = self.get_config("map_path_data", {})
        self.map_path_data = MapPathData(maps=data)

    def _save_path_data(self):
        self.set_config("map_path_data", self.map_path_data.model_dump().get('maps', {}))

    def get_overlay_widget(self):
        return None

    def get_config_widget(self):
        return None

    def start_record(self):
        self.path_builder = PathBuilder(self.path_compose_error_rate)
        self.status = 1

    def stop_record(self):
        self.status = 2

    def do_routine(self, routine_name: str):
        self.replay_status = 1
        routine = self.routine[routine_name]
        for i in range(len(routine) - 1):
            print(f"current map {self.current_map}, routine map {routine[i]}")
            if self.current_map != routine[i]:
                continue
            path = self.map_path_data.maps[routine[i]][routine[i+1]]
            print(f"replay path 【{routine[i]}】 -> 【{routine[i+1]}】")
            self.replay_path(path)
            time.sleep(7)

    def test(self):
        self.do_routine('Martlock -> Thetford')

    def replay_path(self, path):
        for t in path.path:
            print(t)
            while self.pos.distance(t) > self.error_threshold:
                self.keyboard_controller.move(t.x - self.pos.x, t.y - self.pos.y)
            self.pos = t

    def save_check_point(self):
        if self.path_builder.map_name and self.path_builder.end_entrance_name:
            path = self.path_builder.build()
            self.path_builder = PathBuilder(self.path_compose_error_rate)
            self.path_builder.set_start_entrance_name(path.end_entrance_name)
            print(f'[PathRecorderPlugin] save check point {path.map_name} {path.end_entrance_name} {path}')
            if not self.map_path_data.maps.get(path.map_name):
                self.map_path_data.maps[path.map_name] = {}
            self.map_path_data.maps[path.map_name][path.end_entrance_name] = path.__dict__
            self._save_path_data()

    def handle_event(self, event: GameEvent):
        if isinstance(event, MoveRequestEvent):
            self.pos = event.pos
            if self.status == 1:
                self.path_builder.add_point(event.pos)

        if isinstance(event, ChangeClusterResponseEvent):
            if self.status == 1:
                self.path_builder.set_end_entrance_name(event.cluster_name)
                self.save_check_point()
            self.current_map = event.cluster_name
            
        if isinstance(event, JoinFinishResponseEvent):
            if self.status == 1:
                if not self.path_builder.start_entrance_name:
                    self.path_builder.set_start_entrance_name(event.map_name)
                self.path_builder.set_map_name(event.map_name)
                self.save_check_point()
            self.pos = event.new_pos



class MapPath(BaseModel):
    path: list[P] = []
    map_name: str = ''  
    start_pos: P = P()
    end_pos: P = P()
    start_entrance_name: str = ''
    end_entrance_name: str = ''

    def compress(self, error_rate: float=0.2):
        self.path = douglas_peucker(self.path, error_rate)

class MapPathData(BaseModel):
    maps: Dict[str, Dict[str, MapPath]] = Field(default_factory=dict)

class PathBuilder(object):
    def __init__(self, compress_error_rate: float):
        self.path: list[P] = []
        self.map_name: str = ''
        self.start_pos: P = P()
        self.end_pos: P = P()
        self.start_entrance_name: str = ''
        self.end_entrance_name: str = ''
        self.compress_error_rate = compress_error_rate

    def add_point(self, pos: P):
        self.path.append(pos)

    def set_start_pos(self, pos: P):
        self.start_pos = pos

    def set_end_pos(self, pos: P):
        self.end_pos = pos

    def set_start_entrance_name(self, name: str):
        self.start_entrance_name = name

    def set_end_entrance_name(self, name: str):
        self.end_entrance_name = name

    def set_map_name(self, name: str):
        self.map_name = name

    def build(self) -> MapPath:
        map_path = MapPath()
        map_path.path = self.path
        map_path.map_name = self.map_name
        map_path.start_pos = self.start_pos
        map_path.end_pos = self.end_pos
        map_path.start_entrance_name = self.start_entrance_name
        map_path.end_entrance_name = self.end_entrance_name
        if self.compress_error_rate > 0:
            map_path.compress(self.compress_error_rate)
        return map_path
