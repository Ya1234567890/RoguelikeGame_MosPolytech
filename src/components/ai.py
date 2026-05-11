from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from entity import Actor


class BaseAI:
    def __init__(self, entity: Actor):
        self.entity = entity

    def perform(self) -> None:
        raise NotImplementedError()


class HostileEnemy(BaseAI):
    def perform(self) -> None:
        target = self.entity.gamemap.engine.player
        dx = target.x - self.entity.x
        dy = target.y - self.entity.y

        if abs(dx) <= 1 and abs(dy) <= 1:
            self.entity.fighter.attack(target)
        else:
            if dx != 0:
                dx = dx // abs(dx)
            if dy != 0:
                dy = dy // abs(dy)

            dest_x = self.entity.x + dx
            dest_y = self.entity.y + dy

            if self.entity.gamemap.in_bounds(dest_x, dest_y):
                if not self.entity.gamemap.tiles["walkable"][dest_x, dest_y]:
                    return
                if self.entity.gamemap.get_blocking_entity_at_location(dest_x, dest_y):
                    return
                self.entity.move(dx, dy)