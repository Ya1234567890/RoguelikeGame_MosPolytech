from __future__ import annotations

import random
from typing import Iterator, List, TYPE_CHECKING
from components.equipment import Equipment

import tcod

import tile_types
from components.ai import HostileEnemy
from components.fighter import Fighter
from components.inventory import Inventory
from components.consumable import HealingConsumable, LightningDamageConsumable, FireballDamageConsumable
from components.equippable import Equippable   # <-- добавлено
from equipment_types import EquipmentType      # <-- добавлено
from entity import Actor, Item
from game_map import GameMap

if TYPE_CHECKING:
    from engine import Engine


class RectangularRoom:
    def __init__(self, x: int, y: int, width: int, height: int):
        self.x1 = x
        self.y1 = y
        self.x2 = x + width
        self.y2 = y + height

    @property
    def center(self):
        return (self.x1 + self.x2) // 2, (self.y1 + self.y2) // 2

    @property
    def inner(self):
        return slice(self.x1 + 1, self.x2), slice(self.y1 + 1, self.y2)

    def intersects(self, other):
        return (
            self.x1 <= other.x2 and self.x2 >= other.x1 and
            self.y1 <= other.y2 and self.y2 >= other.y1
        )


def place_entities(room: RectangularRoom, dungeon: GameMap, floor_number: int, maximum_monsters: int):
    number_of_monsters = random.randint(0, maximum_monsters)

    for _ in range(number_of_monsters):
        x = random.randint(room.x1 + 1, room.x2 - 1)
        y = random.randint(room.y1 + 1, room.y2 - 1)

        if not any(e.x == x and e.y == y for e in dungeon.entities):
            if random.random() < 0.8:
                fighter = Fighter(hp=10 + floor_number * 2, defense=0 + floor_number, power=3 + floor_number)
                monster = Actor(
                    char="o", color=(63, 127, 63), name="Orc",
                    ai_cls=HostileEnemy, fighter=fighter, inventory=Inventory(capacity=0),
                    equipment=Equipment(),  # <-- у монстров тоже есть экипировка (пустая)
                )
            else:
                if floor_number >= 4:
                    fighter = Fighter(hp=20 + floor_number * 3, defense=2 + floor_number, power=5 + floor_number)
                    monster = Actor(
                        char="D", color=(255, 0, 0), name="Demon",
                        ai_cls=HostileEnemy, fighter=fighter, inventory=Inventory(capacity=0),
                        equipment=Equipment(),
                    )
                elif floor_number >= 2:
                    fighter = Fighter(hp=16 + floor_number * 2, defense=1 + floor_number, power=4 + floor_number)
                    monster = Actor(
                        char="T", color=(0, 127, 0), name="Troll",
                        ai_cls=HostileEnemy, fighter=fighter, inventory=Inventory(capacity=0),
                        equipment=Equipment(),
                    )
                else:
                    fighter = Fighter(hp=10 + floor_number * 2, defense=0 + floor_number, power=3 + floor_number)
                    monster = Actor(
                        char="o", color=(63, 127, 63), name="Orc",
                        ai_cls=HostileEnemy, fighter=fighter, inventory=Inventory(capacity=0),
                        equipment=Equipment(),
                    )
            monster.spawn(dungeon, x, y)


def place_items(room: RectangularRoom, dungeon: GameMap, floor_number: int, maximum_items: int):
    number_of_items = random.randint(0, maximum_items)

    for _ in range(number_of_items):
        x = random.randint(room.x1 + 1, room.x2 - 1)
        y = random.randint(room.y1 + 1, room.y2 - 1)

        if not any(e.x == x and e.y == y for e in dungeon.entities):
            item_chance = random.random()
            if item_chance < 0.5:          # Зелья здоровья
                item = Item(
                    x=x, y=y,
                    char="!",
                    color=(127, 0, 255),
                    name="Health Potion",
                    consumable=HealingConsumable(amount=4 + floor_number * 2),
                )
            elif item_chance < 0.7:        # Свиток молнии
                item = Item(
                    x=x, y=y,
                    char="#",
                    color=(255, 255, 0),
                    name="Lightning Scroll",
                    consumable=LightningDamageConsumable(damage=20 + floor_number * 2, maximum_range=5),
                )
            elif item_chance < 0.85:       # Свиток огненного шара
                item = Item(
                    x=x, y=y,
                    char="#",
                    color=(255, 0, 0),
                    name="Fireball Scroll",
                    consumable=FireballDamageConsumable(damage=12 + floor_number * 2, radius=3),
                )
            else:                          # Экипировка
                equip_type = random.choice([EquipmentType.WEAPON, EquipmentType.ARMOR])
                if equip_type == EquipmentType.WEAPON:
                    power_bonus = random.randint(1, 3 + floor_number // 2)
                    defense_bonus = 0
                    name = "Sword"
                    char = "/"
                    color = (200, 200, 200)
                else:  # броня
                    power_bonus = 0
                    defense_bonus = random.randint(1, 2 + floor_number // 2)
                    name = "Leather Armor"
                    char = "["
                    color = (139, 69, 19)

                equippable = Equippable(
                    equipment_type=equip_type,
                    power_bonus=power_bonus,
                    defense_bonus=defense_bonus,
                )
                item = Item(
                    x=x, y=y,
                    char=char,
                    color=color,
                    name=name,
                    equippable=equippable,
                )
            item.spawn(dungeon, x, y)


def tunnel_between(start, end):
    x1, y1 = start
    x2, y2 = end
    if random.random() < 0.5:
        corner_x, corner_y = x2, y1
    else:
        corner_x, corner_y = x1, y2

    for x, y in tcod.los.bresenham((x1, y1), (corner_x, corner_y)).tolist():
        yield x, y
    for x, y in tcod.los.bresenham((corner_x, corner_y), (x2, y2)).tolist():
        yield x, y


def generate_dungeon(
    max_rooms: int,
    room_min_size: int,
    room_max_size: int,
    map_width: int,
    map_height: int,
    max_monsters_per_room: int,
    max_items_per_room: int,
    engine: Engine,
    floor_number: int = 1,
) -> GameMap:
    """Generate a new dungeon map."""
    player = engine.player
    dungeon = GameMap(engine, map_width, map_height, entities=[player])

    rooms: List[RectangularRoom] = []

    for _ in range(max_rooms):
        room_width = random.randint(room_min_size, room_max_size)
        room_height = random.randint(room_min_size, room_max_size)

        x = random.randint(0, dungeon.width - room_width - 1)
        y = random.randint(0, dungeon.height - room_height - 1)

        new_room = RectangularRoom(x, y, room_width, room_height)

        if any(new_room.intersects(other) for other in rooms):
            continue

        dungeon.tiles[new_room.inner] = tile_types.floor

        if len(rooms) == 0:
            player.place(*new_room.center, dungeon)
        else:
            for tx, ty in tunnel_between(rooms[-1].center, new_room.center):
                dungeon.tiles[tx, ty] = tile_types.floor

        place_entities(new_room, dungeon, floor_number, max_monsters_per_room)
        place_items(new_room, dungeon, floor_number, max_items_per_room)

        rooms.append(new_room)

    if rooms:
        center_of_last_room = rooms[-1].center
        dungeon.tiles[center_of_last_room] = tile_types.down_stairs
        dungeon.downstairs_location = center_of_last_room
    else:
        center = (map_width // 2, map_height // 2)
        dungeon.tiles[...] = tile_types.floor
        player.place(*center, dungeon)
        dungeon.tiles[center] = tile_types.down_stairs
        dungeon.downstairs_location = center

    return dungeon