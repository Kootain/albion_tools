from base.tools import StrEnum
from typing import Dict, Optional
import json
import os

from pydantic import BaseModel

from base.base2 import Item


class Lang(StrEnum):
    en = "EN-US"
    de = "DE-DE"
    fr = "FR-FR"
    ru = "RU-RU"
    pl = "PL-PL"
    es = "ES-ES"
    pt = "PT-BR"
    it = "IT-IT"
    zh_cn = "ZH-CN"
    ko = "KO-KR"
    ja = "JA-JP"
    zh_tw = "ZH-TW"
    id = "ID-ID"
    tr = "TR-TR"
    ar = "AR-SA"

class Item(BaseModel):
    index: int
    name: Optional[Dict[Lang, str]]
    desc: Optional[Dict[Lang, str]]
    name_var: str
    desc_var: str
    unique_name: str

item_idx = {}
item_unique_name = {}

with open(os.path.join(os.path.dirname(__file__), './data/indexedItems.json'), "r", encoding="utf-8") as f:
    raw_items = json.load(f)
    for item in raw_items:
        index = item["Index"]
        localized_names = item["LocalizedNames"]
        localized_descriptions = item["LocalizedDescriptions"]
        name_var = item['LocalizationNameVariable']
        desc_var = item['LocalizationDescriptionVariable']
        unique_name = item['UniqueName']
        i = Item(index=index, name=localized_names, desc=localized_descriptions, name_var=name_var, desc_var=desc_var, unique_name=unique_name)
        item_idx[index] = i
        item_unique_name[unique_name] = i

def get_item(index: int) -> Optional[Item]:
    return item_idx.get(str(index))

def get_item_name(index: int, lang: Lang = Lang.zh_cn) -> str:
    d = f'Unknown({index})'
    item = item_idx.get(str(index))
    if item:
        return item.name.get(lang, item.name.get(Lang.en, d))
    return d

