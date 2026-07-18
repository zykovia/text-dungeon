import random
from collections import deque

from .balance import (
    BASE_MAX_ROOMS,
    BASE_MIN_ROOMS,
    BOSS_ATTACK_RANGE,
    BOSS_HP_RANGE,
    ITEM_SPAWN_CHANCE,
    MAX_DUNGEON_LEVEL,
    MONSTER_SPAWN_CHANCE,
    ROOMS_GROWTH_PER_DUNGEON_LEVEL,
    SUPER_BOSS_ATTACK_RANGE,
    SUPER_BOSS_HP_RANGE,
)
from .directions import DIRECTION_DELTAS, OPPOSITE_DIRECTION
from .models import Item, Monster, Room
from .templates import (
    BOSS,
    ITEM_TEMPLATES,
    MONSTER_TEMPLATES,
    ROOM_TEMPLATES,
    SUPER_BOSS,
    WIN_ITEM_NAME,
)

ENTRANCE_NAME = "Dungeon Entrance"
ENTRANCE_DESCRIPTION = (
    "A crumbling stone archway leads down into darkness. Torches flicker on the walls."
)


def room_count_range(dungeon_level: int) -> tuple[int, int]:
    """Each dungeon level is bigger than the last: +2 rooms (min and max) per level."""
    growth = (dungeon_level - 1) * ROOMS_GROWTH_PER_DUNGEON_LEVEL
    return BASE_MIN_ROOMS + growth, BASE_MAX_ROOMS + growth


def is_final_dungeon(dungeon_level: int) -> bool:
    return dungeon_level >= MAX_DUNGEON_LEVEL


def _bfs_distances(rooms: dict[str, Room], start: str) -> dict[str, int]:
    distances = {start: 0}
    queue = deque([start])
    while queue:
        room_id = queue.popleft()
        for dest in rooms[room_id].exits.values():
            if dest not in distances:
                distances[dest] = distances[room_id] + 1
                queue.append(dest)
    return distances


def generate_dungeon(
    seed: int | None = None,
    min_rooms: int = 6,
    max_rooms: int = 10,
    final_boss: bool = False,
) -> dict[str, Room]:
    """Procedurally build a new dungeon as a self-avoiding random tree on a grid.

    Growing a tree (never reconnecting to an already-placed room) guarantees the
    result stays a consistent grid with no coordinate conflicts, and that every
    room is reachable from "entrance". The farthest room from the entrance becomes
    the boss chamber holding the win condition (the super boss if final_boss is
    set); remaining rooms get a random scattering of monsters and items.
    """
    rng = random.Random(seed)
    num_rooms = rng.randint(min_rooms, max_rooms)

    rooms: dict[str, Room] = {
        "entrance": Room(id="entrance", name=ENTRANCE_NAME, description=ENTRANCE_DESCRIPTION)
    }
    coords = {"entrance": (0, 0)}
    frontier = ["entrance"]
    rooms_needed = num_rooms - 1
    if rooms_needed <= len(ROOM_TEMPLATES):
        room_templates = rng.sample(ROOM_TEMPLATES, rooms_needed)
    else:
        room_templates = rng.choices(ROOM_TEMPLATES, k=rooms_needed)
    next_id = 1

    while len(rooms) < num_rooms and frontier:
        source_id = rng.choice(frontier)
        source_x, source_y = coords[source_id]
        directions = list(DIRECTION_DELTAS)
        rng.shuffle(directions)

        placed = False
        for direction in directions:
            dx, dy = DIRECTION_DELTAS[direction]
            new_coord = (source_x + dx, source_y + dy)
            if new_coord in coords.values():
                continue

            new_id = f"room_{next_id}"
            next_id += 1
            template = room_templates[len(rooms) - 1]
            new_room = Room(id=new_id, name=template.name, description=template.description)
            new_room.exits[OPPOSITE_DIRECTION[direction]] = source_id
            rooms[source_id].exits[direction] = new_id
            rooms[new_id] = new_room
            coords[new_id] = new_coord
            frontier.append(new_id)
            placed = True
            break

        if not placed:
            frontier.remove(source_id)

    distances = _bfs_distances(rooms, "entrance")
    boss_id = max(distances, key=distances.get)
    boss_room = rooms[boss_id]
    if final_boss:
        boss_room.name = SUPER_BOSS.room_name
        boss_room.description = SUPER_BOSS.room_description
        boss_room.monster = Monster(
            SUPER_BOSS.monster_name,
            hp=rng.randint(*SUPER_BOSS_HP_RANGE),
            attack=rng.randint(*SUPER_BOSS_ATTACK_RANGE),
            description=SUPER_BOSS.monster_description,
        )
        crown_description = SUPER_BOSS.crown_description
    else:
        boss_room.name = BOSS.room_name
        boss_room.description = BOSS.room_description
        boss_room.monster = Monster(
            BOSS.monster_name,
            hp=rng.randint(*BOSS_HP_RANGE),
            attack=rng.randint(*BOSS_ATTACK_RANGE),
            description=BOSS.monster_description,
        )
        crown_description = BOSS.crown_description
    boss_room.items = [Item(WIN_ITEM_NAME, crown_description)]

    other_ids = [room_id for room_id in rooms if room_id not in ("entrance", boss_id)]
    for room_id in other_ids:
        room = rooms[room_id]
        if rng.random() < MONSTER_SPAWN_CHANCE:
            monster_template = rng.choice(MONSTER_TEMPLATES)
            room.monster = Monster(
                monster_template.name,
                hp=rng.randint(monster_template.min_hp, monster_template.max_hp),
                attack=monster_template.attack,
                description=monster_template.description,
            )
        if rng.random() < ITEM_SPAWN_CHANCE:
            item_template = rng.choice(ITEM_TEMPLATES)
            room.items.append(
                Item(
                    item_template.name,
                    item_template.description,
                    heal=item_template.heal,
                    damage_bonus=item_template.damage_bonus,
                )
            )

    return rooms
