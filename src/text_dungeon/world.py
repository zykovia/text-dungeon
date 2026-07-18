import random
from collections import deque

from .directions import DIRECTION_DELTAS, OPPOSITE_DIRECTION
from .models import Item, Monster, Room

ENTRANCE_NAME = "Dungeon Entrance"
ENTRANCE_DESCRIPTION = (
    "A crumbling stone archway leads down into darkness. Torches flicker on the walls."
)

ROOM_TEMPLATES = [
    ("Damp Hallway", "Water drips from the ceiling and pools on uneven stone."),
    ("Narrow Passage", "The walls press close enough to brush your shoulders."),
    ("Collapsed Tunnel", "Rubble chokes half the passage; you squeeze through the rest."),
    ("Old Armory", "Rusted weapon racks line the walls, mostly picked clean."),
    ("Forgotten Crypt", "Stone sarcophagi line the walls. Something rattles in the dark."),
    ("Sunken Chamber", "Ankle-deep water reflects your torchlight back at you."),
    ("Guard Post", "An overturned table and scattered bones hint at a losing fight."),
    ("Fungal Grotto", "Pale mushrooms cast a faint glow over slick stone."),
    ("Bone Pit", "A shallow pit crowded with bones, old and new."),
    ("Shrine Room", "A cracked altar stands before a faceless statue."),
]

MONSTER_TEMPLATES = [
    ("skeleton", 8, 12, 2, "A rattling pile of animated bones."),
    ("giant rat", 5, 8, 1, "Its eyes gleam red in the dark."),
    ("cave spider", 6, 9, 2, "Venom drips from its mandibles."),
    ("shade", 9, 13, 3, "A flicker of darkness given cruel shape."),
]

ITEM_TEMPLATES = [
    ("rusty sword", "A worn blade, better than fists.", 0, 2),
    ("health potion", "A vial of red liquid that mends wounds.", 8, 0),
    ("dagger", "Quick and sharp, easy to conceal.", 0, 1),
    ("bandage", "Rough cloth, better than nothing.", 4, 0),
]

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
    room_names = rng.sample(ROOM_TEMPLATES, min(num_rooms - 1, len(ROOM_TEMPLATES)))
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
            name, description = room_names[len(rooms) - 1]
            new_room = Room(id=new_id, name=name, description=description)
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
            name, hp_lo, hp_hi, attack, description = rng.choice(MONSTER_TEMPLATES)
            room.monster = Monster(name, hp=rng.randint(hp_lo, hp_hi), attack=attack, description=description)
        if rng.random() < 0.6:
            name, description, heal, damage_bonus = rng.choice(ITEM_TEMPLATES)
            room.items.append(Item(name, description, heal=heal, damage_bonus=damage_bonus))

    return rooms
