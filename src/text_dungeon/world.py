import random
from collections import deque

from .directions import DIRECTION_DELTAS, OPPOSITE_DIRECTION
from .models import Item, Monster, Room
from .templates import ITEM_TEMPLATES, MONSTER_TEMPLATES, ROOM_TEMPLATES

ENTRANCE_NAME = "Dungeon Entrance"
ENTRANCE_DESCRIPTION = (
    "A crumbling stone archway leads down into darkness. Torches flicker on the walls."
)

BOSS_NAME = "Dungeon Lord"
BOSS_ROOM_NAME = "Throne of the Dungeon Lord"
BOSS_ROOM_DESCRIPTION = "A massive figure sits upon a throne of bones, waiting."
BOSS_DESCRIPTION = "The master of this dungeon, clad in black iron."
WIN_ITEM_NAME = "golden crown"


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
    seed: int | None = None, min_rooms: int = 6, max_rooms: int = 10
) -> dict[str, Room]:
    """Procedurally build a new dungeon as a self-avoiding random tree on a grid.

    Growing a tree (never reconnecting to an already-placed room) guarantees the
    result stays a consistent grid with no coordinate conflicts, and that every
    room is reachable from "entrance". The farthest room from the entrance becomes
    the boss chamber holding the win condition; remaining rooms get a random
    scattering of monsters and items.
    """
    rng = random.Random(seed)
    num_rooms = rng.randint(min_rooms, max_rooms)

    rooms: dict[str, Room] = {
        "entrance": Room(id="entrance", name=ENTRANCE_NAME, description=ENTRANCE_DESCRIPTION)
    }
    coords = {"entrance": (0, 0)}
    frontier = ["entrance"]
    room_templates = rng.sample(ROOM_TEMPLATES, min(num_rooms - 1, len(ROOM_TEMPLATES)))
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
    boss_room.name = BOSS_ROOM_NAME
    boss_room.description = BOSS_ROOM_DESCRIPTION
    boss_room.monster = Monster(
        BOSS_NAME, hp=rng.randint(22, 30), attack=rng.randint(4, 6), description=BOSS_DESCRIPTION
    )
    boss_room.items = [Item(WIN_ITEM_NAME, "The Dungeon Lord's crown. Proof of your victory.")]

    other_ids = [room_id for room_id in rooms if room_id not in ("entrance", boss_id)]
    for room_id in other_ids:
        room = rooms[room_id]
        if rng.random() < 0.5:
            monster_template = rng.choice(MONSTER_TEMPLATES)
            room.monster = Monster(
                monster_template.name,
                hp=rng.randint(monster_template.min_hp, monster_template.max_hp),
                attack=monster_template.attack,
                description=monster_template.description,
            )
        if rng.random() < 0.6:
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
