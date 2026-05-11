from __future__ import annotations

from typing import TYPE_CHECKING

import color
from components.base_component import BaseComponent
from input_handlers import GameOverEventHandler
from render_order import RenderOrder

if TYPE_CHECKING:
    from entity import Actor


class Fighter(BaseComponent):
    entity: Actor

    def __init__(self, hp: int, defense: int, power: int):
        self.max_hp = hp
        self._hp = hp
        self._defense = defense
        self._power = power

    @property
    def hp(self) -> int:
        return self._hp

    @hp.setter
    def hp(self, value: int) -> None:
        self._hp = max(0, min(value, self.max_hp))
        if self._hp == 0 and self.entity.ai:
            self.die()

    @property
    def power(self) -> int:
        """Сила атаки с учётом экипировки."""
        base_power = self._power
        if self.entity.is_alive and hasattr(self.entity, 'equipment'):
            return base_power + self.entity.equipment.power_bonus
        return base_power

    @property
    def defense(self) -> int:
        """Защита с учётом экипировки."""
        base_defense = self._defense
        if self.entity.is_alive and hasattr(self.entity, 'equipment'):
            return base_defense + self.entity.equipment.defense_bonus
        return base_defense

    def heal(self, amount: int) -> int:
        if self.hp == self.max_hp:
            return 0
        new_hp_value = self.hp + amount
        if new_hp_value > self.max_hp:
            new_hp_value = self.max_hp
        amount_recovered = new_hp_value - self.hp
        self.hp = new_hp_value
        return amount_recovered

    def die(self) -> None:
        if self.engine.player is self.entity:
            death_message = "You died!"
            death_message_color = color.player_die
            self.engine.event_handler = GameOverEventHandler(self.engine)
        else:
            death_message = f"{self.entity.name} is dead!"
            death_message_color = color.enemy_die

        self.entity.char = "%"
        self.entity.color = (191, 0, 0)
        self.entity.blocks_movement = False
        self.entity.ai = None
        self.entity.name = f"remains of {self.entity.name}"
        self.entity.render_order = RenderOrder.CORPSE

        self.engine.message_log.add_message(death_message, death_message_color)

    def attack(self, target: Actor) -> None:
        damage = self.power - target.fighter.defense
        attack_desc = f"{self.entity.name.capitalize()} attacks {target.name}"

        if self.entity is self.engine.player:
            attack_color = color.player_atk
        else:
            attack_color = color.enemy_atk

        if damage > 0:
            self.engine.message_log.add_message(
                f"{attack_desc} for {damage} hit points.", attack_color
            )
            target.fighter.hp -= damage
        else:
            self.engine.message_log.add_message(
                f"{attack_desc} but does no damage.", attack_color
            )