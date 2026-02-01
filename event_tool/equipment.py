from typing import List
from base.base2 import Equipment, Item, SlotType

slot_spelles_idx = {
    SlotType.MainHand: [0, 1, 2],
    SlotType.Chest: [3],
    SlotType.Head: [4],
    SlotType.Shoes: [5],
    SlotType.Potion: [12],
    SlotType.BuffFood: [13],
}

def parses_equipments(eqs: List[int], sps: List[int]) -> Equipment:
    equipment = Equipment()
    def v(i: int) -> int:
        return int(eqs[i]) if i < len(eqs) else 0
    equipment.main_hand = Item(slot_type=SlotType.MainHand, index=v(0))
    equipment.off_hand = Item(slot_type=SlotType.OffHand, index=v(1))
    equipment.head = Item(slot_type=SlotType.Head, index=v(2))
    equipment.chest = Item(slot_type=SlotType.Chest, index=v(3))
    equipment.shoes = Item(slot_type=SlotType.Shoes, index=v(4))
    equipment.bag = Item(slot_type=SlotType.Bag, index=v(5))
    equipment.cape = Item(slot_type=SlotType.Cape, index=v(6))
    equipment.mount = Item(slot_type=SlotType.Mount, index=v(7))
    equipment.potion = Item(slot_type=SlotType.Potion, index=v(8))
    equipment.buff_food = Item(slot_type=SlotType.BuffFood, index=v(9))
    def set_spells(item: Item, idxs: List[int]):
        item.spells = [int(sps[idx]) for idx in idxs if idx < len(sps) and int(sps[idx]) != 0]
    set_spells(equipment.main_hand, slot_spelles_idx.get(SlotType.MainHand, []))
    set_spells(equipment.chest, slot_spelles_idx.get(SlotType.Chest, []))
    set_spells(equipment.head, slot_spelles_idx.get(SlotType.Head, []))
    set_spells(equipment.shoes, slot_spelles_idx.get(SlotType.Shoes, []))
    set_spells(equipment.potion, slot_spelles_idx.get(SlotType.Potion, []))
    set_spells(equipment.buff_food, slot_spelles_idx.get(SlotType.BuffFood, []))
    return equipment
