 
from base.plugin import BasePlugin
from base.base2 import GameEvent, Entity
from base.event_codes import EventCodes, EventType
from ui.panels.log_panel import LogPanel
from ui.panels.player_monitor_panel import PlayerMonitorPanel
from core.events.event.new_characters import NewCharacterEvent
from core.events.event.spell import CastStartEvent
import time
from game_data.spells import get_spell_by_index
from game_data.items import get_item_name
from collections import OrderedDict


class PlayerPlugin(BasePlugin):

    def __init__(self):
        super().__init__("player", "玩家追踪")
        self._config_widget = None
        self._players = OrderedDict() # LRU Cache: name -> player_data
        self._max_cache_size = 500


    def get_overlay_widget(self):
        return None

    def get_config_widget(self):
        if not self._config_widget:
            self._config_widget = PlayerMonitorPanel()
            
            # Load config from BasePlugin storage
            monitor_config = self.get_config("monitor_settings", {})
            self._config_widget.load_config(monitor_config)
            
            # Connect save signal
            self._config_widget.save_requested.connect(self._on_save_monitor_config)
            
            # Restore cached data if any
            for player_data in self._players.values():
                self._config_widget.add_player(player_data)
        return self._config_widget

    def _on_save_monitor_config(self, config_data):
        self.set_config("monitor_settings", config_data)

    def handle_event(self, event: GameEvent):
        if isinstance(event, NewCharacterEvent):
            self._update_player_data(event.entity)

        if isinstance(event, CastStartEvent):
            spell = get_spell_by_index(event.spell_id)
            if self._config_widget:
                if spell:
                    # Find player name from OID
                    player_name = None
                    for p in self._players.values():
                        if p["oid"] == event.oid:
                            player_name = p["name"]
                            break
                    
                    if player_name:
                        self._config_widget.trigger_skill_alert(player_name, event.spell_id, spell.name_locatag)

    def _update_player_data(self, entity: Entity):
        # Format data for PlayerMonitorPanel
        
        # Ensure name is clean
        raw_name = entity.name
        if not raw_name:
            return
        name = str(raw_name).strip()

        player_data = {
            "oid": entity.oid,
            "name": name,
            "guild": entity.guild,
            "alliance": "", 
            "equipment": {}
        }

        # Helper to format item data
        def format_item(item):
            if not item or item.index == 0:
                return None
            
            # get_item_name returns str, need to check if it returns unique_name or localized name?
            # looking at plugin.py imports: from game_data.items import get_item_name
            # usually get_item_name returns localized name.
            # We need unique_name for armor type detection in UI.
            # Let's check game_data.items.py again if needed, but I recall get_item_name returns name.
            # Wait, PlayerMonitorPanel expects "unique_name" for armor type.
            # And "name" for display.
            # We need a way to get unique_name from index.
            # I should import get_item_unique_name if available or access item_idx directly?
            # Re-checking game_data/items.py in my memory/search...
            # Previous Read of game_data/items.py showed:
            # item_idx = {} ... Item(index, name, ..., unique_name)
            # So I can access item_idx to get unique_name.
            
            from game_data.items import item_idx, get_item_name as get_loc_name
            
            item_info = item_idx.get(str(item.index)) or item_idx.get(item.index)
            unique_name = item_info.unique_name if item_info else ""
            name = get_loc_name(item.index)
            
            spells = []
            for spell_id in item.spells:
                s = get_spell_by_index(spell_id)
                if s:
                    # Append tuple (spell_id, spell_name)
                    spells.append((spell_id, s.name_locatag)) 
            
            return {
                "name": name,
                "unique_name": unique_name,
                "spells": spells # List of (id, name) tuples
            }

        equip = entity.equipment
        player_data["equipment"] = {
            "main_hand": format_item(equip.main_hand),
            "off_hand": format_item(equip.off_hand),
            "head": format_item(equip.head),
            "chest": format_item(equip.chest), # UI uses 'armor' key? Let's check UI.
            # UI PlayerMonitorPanel uses "armor" key for chest/armor slot?
            # Let's check PlayerMonitorPanel.slots: "armor": (1, 1, "胸甲")
            # So yes, key is "armor". But Entity has "chest".
            "armor": format_item(equip.chest), 
            "shoes": format_item(equip.shoes),
            "bag": format_item(equip.bag),
            "cape": format_item(equip.cape),
            "potion": format_item(equip.potion),
            "food": format_item(equip.buff_food)
        }

        # Cache Logic (LRU by name)
        key = name
        if key in self._players:
            self._players.move_to_end(key)
        self._players[key] = player_data
        
        if len(self._players) > self._max_cache_size:
            self._players.popitem(last=False) # Remove first (oldest)

        # Update UI if initialized
        if self._config_widget:
            self._config_widget.add_player(player_data)

    def _log_new_character(self, entity):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        main_hand_item = get_item_name(entity.equipment.main_hand.index)
        head_item = get_item_name(entity.equipment.head.index)
        chest_item = get_item_name(entity.equipment.chest.index)
        shoes_item = get_item_name(entity.equipment.shoes.index)
        main_hand_spells = [get_spell_by_index(idx).name_locatag for idx in entity.equipment.main_hand.spells]
        head_spells = [get_spell_by_index(idx).name_locatag for idx in entity.equipment.head.spells]
        chest_spells = [get_spell_by_index(idx).name_locatag for idx in entity.equipment.chest.spells]
        shoes_spells = [get_spell_by_index(idx).name_locatag for idx in entity.equipment.shoes.spells]
        print(f"[{timestamp}]===============")
        print(f"Player: {entity.name} {entity.oid}")
        print(f"MainHand: {main_hand_item} {main_hand_spells}")
        print(f"Head: {head_item} {head_spells}")
        print(f"Chest: {chest_item} {chest_spells}")
        print(f"Shoes: {shoes_item} {shoes_spells}") 

    def _log_cast_start(self, event):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        print(f"[{timestamp}]===============")
        print(f"Player: {event.oid}")
        print(f"Spell: {get_spell_by_index(event.spell_id).name_locatag}")

