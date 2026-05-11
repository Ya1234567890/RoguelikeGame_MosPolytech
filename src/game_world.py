from __future__ import annotations

from typing import TYPE_CHECKING

from procgen import generate_dungeon

if TYPE_CHECKING:
    from engine import Engine


class GameWorld:
    def __init__(self, engine: Engine, map_width: int, map_height: int, max_rooms: int,
                 room_min_size: int, room_max_size: int, max_monsters_per_room: int, max_items_per_room: int):
        self.engine = engine
        self.map_width = map_width
        self.map_height = map_height
        self.max_rooms = max_rooms
        self.room_min_size = room_min_size
        self.room_max_size = room_max_size
        self.max_monsters_per_room = max_monsters_per_room
        self.max_items_per_room = max_items_per_room
        self.current_floor = 0

    def generate_floor(self) -> None:
        self.current_floor += 1
        self.engine.game_map = generate_dungeon(
            max_rooms=self.max_rooms,
            room_min_size=self.room_min_size,
            room_max_size=self.room_max_size,
            map_width=self.map_width,
            map_height=self.map_height,
            max_monsters_per_room=self.max_monsters_per_room,
            max_items_per_room=self.max_items_per_room,
            engine=self.engine,
            floor_number=self.current_floor,
        )