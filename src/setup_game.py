"""Setup that is shared between main.py and the save/load routines."""
import lzma
import pickle

import color
from engine import Engine
from entity import Actor
from components.ai import HostileEnemy
from components.fighter import Fighter
from components.inventory import Inventory
from components.equipment import Equipment
from components.equippable import Equippable
from equipment_types import EquipmentType
from game_world import GameWorld
from input_handlers import MainGameEventHandler
from procgen import generate_dungeon
from entity import Actor, Item

def new_game() -> Engine:
    map_width = 80
    map_height = 43
    room_max_size = 10
    room_min_size = 6
    max_rooms = 30
    max_monsters_per_room = 2
    max_items_per_room = 2

    # Создаём компоненты игрока
    fighter = Fighter(hp=30, defense=2, power=5)
    inventory = Inventory(capacity=26)
    equipment = Equipment()

    player = Actor(
        char="@",
        color=(255, 255, 255),
        name="Player",
        ai_cls=HostileEnemy,
        fighter=fighter,
        inventory=inventory,
        equipment=equipment,
    )

    dagger = Item(
        char="/",
        color=(200, 200, 200),
        name="Dagger",
        equippable=Equippable(EquipmentType.WEAPON, power_bonus=1),
    )
    player.inventory.items.append(dagger)

    engine = Engine(player=player)
    engine.game_world = GameWorld(
        engine=engine,
        map_width=map_width,
        map_height=map_height,
        max_rooms=max_rooms,
        room_min_size=room_min_size,
        room_max_size=room_max_size,
        max_monsters_per_room=max_monsters_per_room,
        max_items_per_room=max_items_per_room,
    )
    engine.game_world.generate_floor()  # первый уровень
    engine.update_fov()
    engine.message_log.add_message(
        "Hello and welcome, adventurer, to yet another dungeon!", color.welcome_text
    )
    return engine


def load_game(engine: Engine, filename: str) -> None:
    with open(filename, "rb") as f:
        loaded_engine = pickle.loads(lzma.decompress(f.read()))
    assert isinstance(loaded_engine, Engine)

    engine.game_map = loaded_engine.game_map
    engine.player = loaded_engine.player
    engine.message_log = loaded_engine.message_log
    engine.mouse_location = loaded_engine.mouse_location
    engine.game_world = loaded_engine.game_world
    engine.game_world.engine = engine

    engine.game_map.engine = engine
    engine.game_map.restore_entity_gamemap()

    for item in engine.player.inventory.items:
        item.gamemap = engine.game_map
        if hasattr(item, 'consumable') and item.consumable:
            item.consumable.entity = item
        if hasattr(item, 'equippable') and item.equippable:   # <-- восстанавливаем связь
            item.equippable.entity = item

    # Восстанавливаем связь экипировки с игроком
    if hasattr(engine.player, 'equipment') and engine.player.equipment:
        engine.player.equipment.parent = engine.player
        if engine.player.equipment.weapon:
            engine.player.equipment.weapon.equippable.entity = engine.player.equipment.weapon
        if engine.player.equipment.armor:
            engine.player.equipment.armor.equippable.entity = engine.player.equipment.armor

    engine.event_handler = MainGameEventHandler(engine)
    engine.update_fov()
    engine.message_log.add_message("Game loaded.", color.white)