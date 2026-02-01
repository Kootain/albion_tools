from collections import defaultdict
import json
import os

class Localization(object):
    def __init__(self):
        self.items = {}
        self.spells = {}
        self.shop_category = {}
        self.destiny_board = {}
        self.journal = {}
        self.sa = {}
    
    def get_spell_name(self, spell_uid: str, lang: str = 'ZH-CN') -> str:
        return self.spells.get(spell_uid, {}).get(lang, '')

    def get_spell_desc(self, spell_uid: str, lang: str = 'ZH-CN') -> str:
        return self.spells.get(f'{spell_uid}_DESC', {}).get(lang, '')

localization = Localization()

def load():
    global localization
    with open(os.path.join(os.path.dirname(__file__), './data/merged_localization.json'), 'r', encoding='utf-8') as f:
        raw = json.load(f)
    for d in raw:
        tuid = d['@tuid']
        tuv = {}
        lang_data = d.get('tuv', [])
        if isinstance(lang_data, dict):
            lang_data = [lang_data]
        for i in lang_data:
            tuv[i['@xml:lang']] = i['seg']
        prefix = tuid.split('_')[0]
        trimd_id = tuid[len(prefix)+1:]
        if prefix == 'ITEMS':
            localization.items[trimd_id] = tuv
        elif prefix == 'SPELLS':
            localization.spells[trimd_id] = tuv
        elif prefix == 'SHOPCATEGORY':
            localization.shop_category[trimd_id] = tuv
        elif prefix == 'DESTINYBOARD':
            localization.destiny_board[trimd_id] = tuv
        elif prefix == 'JOURNAL':
            localization.journal[trimd_id] = tuv
        elif prefix == 'SA':
            localization.sa[trimd_id] = tuv

load()