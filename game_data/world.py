from pydantic import BaseModel
import json
import os

class WorldData(BaseModel):
    raw: dict
    displayname: str
    id: str    

def isalpha(c):
    return 'a' <= c <= 'z' or 'A' <= c <= 'Z' or c == ' ' or c in ['\'', '.']

with open(os.path.join(os.path.dirname(__file__), './data/world.json'), 'r', encoding='utf-8-sig') as f:
    data = json.load(f)

map_data = {}
for d in data:
    map_data[d['@id']] = d

for d in data:
    displayname = d.get('@displayname')
    map_id = d.get('@id')
    # for l in displayname:
        # if not isalpha(l):
        #     print(f'{k}:{displayname}')
        #     break
    map_data[map_id] = WorldData(
        raw=d,
        displayname=displayname,
        id=map_id
    )



def get_map(map_id: int) -> WorldData:
    return map_data.get(map_id, WorldData(
        raw={},
        displayname="Unknown",
        id="Unknown"
    ))