from __future__ import annotations

from typing import Callable, Optional, TYPE_CHECKING

import color
from actions import ItemAction
from components.base_component import BaseComponent
from components.inventory import Inventory
from exceptions import Impossible
from input_handlers import SelectIndexHandler, MainGameEventHandler

if TYPE_CHECKING:
    from entity import Actor, Item
    from engine import Engine


class Consumable(BaseComponent):
    entity: Item

    def get_action(self, consumer: Actor) -> Optional[Action]:
        return ItemAction(consumer, self.entity)

    def activate(self, action: ItemAction) -> None:
        raise NotImplementedError()

    def consume(self) -> None:
        """Remove the consumed item from its containing inventory."""
        entity = self.entity
        inventory = entity.parent
        if isinstance(inventory, Inventory):
            inventory.items.remove(entity)


class HealingConsumable(Consumable):
    def __init__(self, amount: int):
        self.amount = amount

    def activate(self, action: ItemAction) -> None:
        consumer = action.entity
        amount_recovered = consumer.fighter.heal(self.amount)

        if amount_recovered > 0:
            self.engine.message_log.add_message(
                f"You consume the {self.entity.name}, and recover {amount_recovered} HP!",
                color.health_recovered,
            )
            self.consume()
        else:
            raise Impossible(f"Your health is already full.")


class LightningDamageConsumable(Consumable):
    def __init__(self, damage: int, maximum_range: int):
        self.damage = damage
        self.maximum_range = maximum_range

    def activate(self, action: ItemAction) -> None:
        consumer = action.entity
        target = None
        closest_distance = self.maximum_range + 1.0

        for actor in self.engine.game_map.actors:
            if actor is not consumer and self.engine.game_map.visible[actor.x, actor.y]:
                distance = consumer.distance(actor.x, actor.y)

                if distance < closest_distance:
                    target = actor
                    closest_distance = distance

        if target:
            self.engine.message_log.add_message(
                f"A lighting bolt strikes the {target.name} with a loud thunder, for {self.damage} damage!"
            )
            target.fighter.hp -= self.damage
            self.consume()
        else:
            raise Impossible("No enemy is close enough to strike.")


class FireballDamageConsumable(Consumable):
    def __init__(self, damage: int, radius: int):
        self.damage = damage
        self.radius = radius

    def get_action(self, consumer: Actor) -> Optional[Action]:
        self.engine.message_log.add_message(
            "Select a target location.", color.needs_target
        )
        self.engine.event_handler = AreaRangedAttackHandler(
            self.engine,
            radius=self.radius,
            callback=lambda xy: ItemAction(consumer, self.entity, xy),
        )
        return None

    def activate(self, action: ItemAction) -> None:
        target_xy = action.target_xy

        if not self.engine.game_map.visible[target_xy]:
            raise Impossible("You cannot target an area that you cannot see.")

        targets_hit = False
        for actor in self.engine.game_map.actors:
            if actor.distance(*target_xy) <= self.radius:
                self.engine.message_log.add_message(
                    f"The {actor.name} is engulfed in a fiery explosion, taking {self.damage} damage!"
                )
                actor.fighter.hp -= self.damage
                targets_hit = True

        if not targets_hit:
            raise Impossible("There are no targets in the radius.")
        self.consume()


class AreaRangedAttackHandler(SelectIndexHandler):
    """Handles targeting an area within a given radius."""

    def __init__(self, engine: Engine, radius: int, callback: Callable[[Tuple[int, int]], Optional[Action]]):
        super().__init__(engine)
        self.radius = radius
        self.callback = callback

    def on_render(self, console: tcod.Console) -> None:
        """Highlight the tile under the cursor."""
        super().on_render(console)
        x, y = self.engine.mouse_location
        console.draw_frame(
            x=x - self.radius,
            y=y - self.radius,
            width=self.radius * 2 + 1,
            height=self.radius * 2 + 1,
            fg=color.red,
            clear=False,
        )

    def on_index_selected(self, x: int, y: int) -> Optional[Action]:
        self.engine.event_handler = MainGameEventHandler(self.engine)
        action = self.callback((x, y))
        if action:
            try:
                action.perform()
                self.engine.handle_enemy_turns()
                self.engine.update_fov()
            except Impossible as exc:
                self.engine.message_log.add_message(exc.args[0], color.impossible)
        return None