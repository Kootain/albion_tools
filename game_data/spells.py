import os
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import List, Optional
from game_data.localization import localization


@dataclass
class GameFileDataSpell:
    index: int = -1
    unique_name: str = ""
    target: str = ""
    category: str = ""
    name_locatag: str = ""
    description_locatag: str = ""


_spells: List[GameFileDataSpell] = []


def get_unique_name(index: int) -> str:
    s = get_spell_by_index(index)
    return s.unique_name if s else ""


def is_data_loaded() -> bool:
    return len(_spells) > 0


def get_spell_by_index(index: int) -> Optional[GameFileDataSpell]:
    if not is_data_loaded():
        return GameFileDataSpell()
    if index < 0:
        index = (index + (1 << 32)) & 0xFFFFFFFF
    if 0 <= index < len(_spells):
        return _spells[index]
    return GameFileDataSpell()



def load_data() -> bool:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "data", "spells.xml")
    if not os.path.exists(file_path):
        _spells.clear()
        return False
    root = ET.parse(file_path).getroot()
    elements = list(root)
    spells = build_spells(elements)
    _spells.clear()
    _spells.extend(spells)
    return len(_spells) >= 0


def build_spells(elements: List[ET.Element]) -> List[GameFileDataSpell]:
    spells: List[GameFileDataSpell] = []
    index = 0
    for el in elements:
        tag = _strip_ns(el.tag)
        if tag == "colortag":
            pass
        elif tag == "passivespell":
            s = _create_game_file_data_spell(index, el)
            index += 1
            if s:
                spells.append(s)
        elif tag == "activespell":
            s = _create_game_file_data_spell(index, el)
            index += 1
            if s:
                spells.append(s)
            if el.find("channelingspell") is not None:
                cs = _create_game_file_data_spell(index, el)
                index += 1
                if cs:
                    spells.append(cs)
        elif tag == "togglespell":
            s = _create_game_file_data_spell(index, el)
            index += 1
            if s:
                spells.append(s)
        else:
            raise ValueError("Invalid spell element")
    return spells


def _create_game_file_data_spell(index: int, el: ET.Element) -> Optional[GameFileDataSpell]:
    unique_name = _get_attr(el, "uniquename")
    name_locatag = _get_attr(el, "namelocatag")
    description_locatag = _get_attr(el, "descriptionlocatag")
    target = _get_attr(el, "target")
    category = _get_attr(el, "category")
    name_locatag = localization.get_spell_name(unique_name) or name_locatag
    description_locatag = localization.get_spell_desc(unique_name) or description_locatag
    if unique_name:
        return GameFileDataSpell(
            index=index,
            unique_name=unique_name,
            target=target,
            category=category,
            name_locatag=name_locatag,
            description_locatag=description_locatag,
        )
    return None


def _get_attr(el: ET.Element, name: str) -> str:
    v = el.get(name)
    return v if v is not None else ""


def _strip_ns(tag: str) -> str:
    if "}" in tag:
        return tag.split("}", 1)[1]
    return tag

load_data()