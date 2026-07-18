from collections import deque

from .models import Item, Monster, Room

DIRECTION_DELTAS = {"north": (0, 1), "south": (0, -1), "east": (1, 0), "west": (-1, 0)}


def compute_coords(rooms: dict[str, Room], start: str = "entrance") -> dict[str, tuple[int, int]]:
    """Derive grid coordinates for each room by walking cardinal exits from `start`.

    Assumes the exit graph is a consistent planar grid (as built by build_world) —
    a room reached two different ways would silently keep whichever coordinate it
    got first.
    """
    coords = {start: (0, 0)}
    queue = deque([start])
    while queue:
        room_id = queue.popleft()
        x, y = coords[room_id]
        for direction, dest in rooms[room_id].exits.items():
            delta = DIRECTION_DELTAS.get(direction)
            if delta is None or dest in coords:
                continue
            coords[dest] = (x + delta[0], y + delta[1])
            queue.append(dest)
    return coords


def build_world() -> dict[str, Room]:
    return {
        "entrance": Room(
            id="entrance",
            name="Dungeon Entrance",
            description=(
                "A crumbling stone archway leads down into darkness. "
                "Torches flicker on the walls."
            ),
            exits={"north": "hallway"},
        ),
        "hallway": Room(
            id="hallway",
            name="Damp Hallway",
            description=(
                "Water drips from the ceiling. Passages lead north and east, "
                "and south back outside."
            ),
            exits={"north": "armory", "east": "crypt", "south": "entrance"},
        ),
        "armory": Room(
            id="armory",
            name="Old Armory",
            description="Rusted weapon racks line the walls, mostly picked clean.",
            exits={"south": "hallway"},
            items=[Item("rusty sword", "A worn blade, better than fists.", damage_bonus=2)],
        ),
        "crypt": Room(
            id="crypt",
            name="Forgotten Crypt",
            description="Stone sarcophagi line the walls. Something rattles in the dark.",
            exits={"west": "hallway", "north": "boss_chamber"},
            items=[Item("health potion", "A vial of red liquid that mends wounds.", heal=8)],
            monster=Monster(
                "skeleton", hp=10, attack=2, description="A rattling pile of animated bones."
            ),
        ),
        "boss_chamber": Room(
            id="boss_chamber",
            name="Throne of the Dungeon Lord",
            description="A massive figure sits upon a throne of bones, waiting.",
            exits={"south": "crypt"},
            items=[Item("golden crown", "The Dungeon Lord's crown. Proof of your victory.")],
            monster=Monster(
                "Dungeon Lord",
                hp=25,
                attack=5,
                description="The master of this dungeon, clad in black iron.",
            ),
        ),
    }
