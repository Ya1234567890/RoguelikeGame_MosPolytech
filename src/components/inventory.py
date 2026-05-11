from __future__ import annotations

from typing import List, TYPE_CHECKING

from components.base_component import BaseComponent

if TYPE_CHECKING:
    from entity import Actor, Item


class Inventory(BaseComponent):
    parent: Actor

    def __init__(self, capacity: int):
        self.capacity = capacity
        self.items: List[Item] = []

    @property
    def entity(self) -> Actor:
        return self.parent

    def drop(self, item: Item) -> None:
        """Removes an item from the inventory and places it on the ground."""
        # Если предмет был экипирован — снимаем его
        if self.parent.equipment:
            if self.parent.equipment.weapon == item:
                self.parent.equipment.toggle_equip(item, add_message=False)
            elif self.parent.equipment.armor == item:
                self.parent.equipment.toggle_equip(item, add_message=False)

        self.items.remove(item)
        item.x = self.parent.x
        item.y = self.parent.y
        item.parent = None
        item.gamemap = self.parent.gamemap
        self.parent.gamemap.entities.add(item)
        self.engine.message_log.add_message(f"You dropped the {item.name}.")

    def equip(self, item: Item) -> None:
        """Экипировать предмет (если он может быть экипирован)."""
        if not item.equippable:
            self.engine.message_log.add_message(f"{item.name} нельзя экипировать.")
            return

        self.parent.equipment.toggle_equip(item)

    def unequip(self, item: Item) -> None:
        """Снять предмет (если он экипирован)."""
        self.parent.equipment.toggle_equip(item)