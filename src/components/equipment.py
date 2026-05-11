from __future__ import annotations
from typing import Optional, TYPE_CHECKING

from components.base_component import BaseComponent
from equipment_types import EquipmentType

if TYPE_CHECKING:
    from entity import Actor, Item


class Equipment(BaseComponent):
    parent: Actor

    def __init__(self, weapon: Optional[Item] = None, armor: Optional[Item] = None):
        self.weapon = weapon
        self.armor = armor

    @property
    def entity(self) -> Actor:
        """Возвращает владельца экипировки."""
        return self.parent

    @property
    def defense_bonus(self) -> int:
        bonus = 0
        if self.weapon and self.weapon.equippable:
            bonus += self.weapon.equippable.defense_bonus
        if self.armor and self.armor.equippable:
            bonus += self.armor.equippable.defense_bonus
        return bonus

    @property
    def power_bonus(self) -> int:
        bonus = 0
        if self.weapon and self.weapon.equippable:
            bonus += self.weapon.equippable.power_bonus
        if self.armor and self.armor.equippable:
            bonus += self.armor.equippable.power_bonus
        return bonus

    def toggle_equip(self, item: Item, add_message: bool = True) -> None:
        """Экипировать или снять предмет."""
        from components.equippable import Equippable

        if not isinstance(item.equippable, Equippable):
            if add_message:
                self.engine.message_log.add_message(
                    f"Нельзя экипировать {item.name}."
                )
            return

        if item.equippable.equipment_type == EquipmentType.WEAPON:
            if self.weapon == item:
                self.weapon = None
                if add_message:
                    self.engine.message_log.add_message(f"Вы сняли {item.name}.")
            else:
                if self.weapon:
                    self.toggle_equip(self.weapon, add_message=False)
                self.weapon = item
                if add_message:
                    self.engine.message_log.add_message(f"Вы экипировали {item.name}.")
        elif item.equippable.equipment_type == EquipmentType.ARMOR:
            if self.armor == item:
                self.armor = None
                if add_message:
                    self.engine.message_log.add_message(f"Вы сняли {item.name}.")
            else:
                if self.armor:
                    self.toggle_equip(self.armor, add_message=False)
                self.armor = item
                if add_message:
                    self.engine.message_log.add_message(f"Вы экипировали {item.name}.")