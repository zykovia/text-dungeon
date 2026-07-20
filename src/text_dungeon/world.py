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
from .items import item_from_template
from .models import Item, Monster, Room
from .templates import (
    BOSS,
    ITEM_TEMPLATES,
    MAX_ITEM_TIER,
    MONSTER_TEMPLATES,
    POTION_TEMPLATES,
    ROOM_TEMPLATES,
    SUPER_BOSS,
    WIN_ITEM_NAME,
    item_template_for,
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


def _has_foreign_neighbor(
    coord: tuple[int, int], source_id: str, room_at_coord: dict[tuple[int, int], str]
) -> bool:
    """True if some room other than `source_id` already occupies a cell next to `coord`."""
    x, y = coord
    for dx, dy in DIRECTION_DELTAS.values():
        occupant = room_at_coord.get((x + dx, y + dy))
        if occupant is not None and occupant != source_id:
            return True
    return False


def _pick_item_template(
    rng: random.Random,
    player_class: str | None,
    upgrade_slot: str | None,
    upgrade_tier: int | None,
):
    """Pick a template for a spawned item.

    With no player context (used by callers that generate class-agnostic
    dungeons), fall back to a uniform pick across every item. Otherwise, offer
    a chance at the player's next weapon/off-hand upgrade for whichever slot
    is due this dungeon, alongside the usual potions.
    """
    if player_class is None:
        return rng.choice(ITEM_TEMPLATES)

    candidates = list(POTION_TEMPLATES)
    if upgrade_tier is not None and upgrade_tier <= MAX_ITEM_TIER:
        upgrade = item_template_for(player_class, upgrade_slot, upgrade_tier)
        if upgrade is not None:
            candidates.append(upgrade)
    return rng.choice(candidates)


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
    player_class: str | None = None,
    upgrade_slot: str | None = None,
    upgrade_tier: int | None = None,
) -> dict[str, Room]:
    """Procedurally build a new dungeon as a self-avoiding random tree on a grid.

    Growing a tree (never reconnecting to an already-placed room) guarantees the
    result stays a consistent grid with no coordinate conflicts, and that every
    room is reachable from "entrance". A new room is also rejected if it would
    land grid-adjacent to any room other than the one it's branching off of, so
    two rooms are never drawn touching on the minimap unless an exit actually
    connects them. The room farthest from the entrance (or the next-farthest,
    if it has no free cell to expand into) becomes the boss chamber (the super
    boss if final_boss is set), and a vault room holding the win condition is
    attached beyond it, reachable only by passing through the boss. Remaining
    rooms get a random scattering of monsters and items: with a player_class
    given, item spawns favor that class's next weapon/off-hand upgrade for
    whichever slot (upgrade_slot, at upgrade_tier) is due this dungeon.
    """
    rng = random.Random(seed)
    num_rooms = rng.randint(min_rooms, max_rooms)

    rooms: dict[str, Room] = {
        "entrance": Room(id="entrance", name=ENTRANCE_NAME, description=ENTRANCE_DESCRIPTION)
    }
    coords = {"entrance": (0, 0)}
    room_at_coord = {(0, 0): "entrance"}
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
            if new_coord in room_at_coord:
                continue
            if _has_foreign_neighbor(new_coord, source_id, room_at_coord):
                continue

            new_id = f"room_{next_id}"
            next_id += 1
            template = room_templates[len(rooms) - 1]
            new_room = Room(id=new_id, name=template.name, description=template.description)
            new_room.exits[OPPOSITE_DIRECTION[direction]] = source_id
            rooms[source_id].exits[direction] = new_id
            rooms[new_id] = new_room
            coords[new_id] = new_coord
            room_at_coord[new_coord] = new_id
            frontier.append(new_id)
            placed = True
            break

        if not placed:
            frontier.remove(source_id)

    # The boss guards the room farthest from the entrance. If that room has no
    # free adjacent cell, fall back to the next-farthest room instead, so a
    # vault can always be attached beyond the boss.
    distances = _bfs_distances(rooms, "entrance")
    candidates = sorted(distances, key=distances.get, reverse=True)
    boss_id = candidates[0]
    vault_direction = None
    vault_coord = None
    for candidate_id in candidates:
        cx, cy = coords[candidate_id]
        directions = list(DIRECTION_DELTAS)
        rng.shuffle(directions)
        for direction in directions:
            dx, dy = DIRECTION_DELTAS[direction]
            new_coord = (cx + dx, cy + dy)
            if new_coord in room_at_coord:
                continue
            if _has_foreign_neighbor(new_coord, candidate_id, room_at_coord):
                continue
            boss_id = candidate_id
            vault_direction = direction
            vault_coord = new_coord
            break
        if vault_direction is not None:
            break

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
        vault_name = SUPER_BOSS.vault_room_name
        vault_description = SUPER_BOSS.vault_room_description
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
        vault_name = BOSS.vault_room_name
        vault_description = BOSS.vault_room_description

    # The crown lives in its own vault beyond the boss chamber, so the only
    # way to reach it is to walk through (and thus defeat) the boss first.
    if vault_coord is not None:
        vault_id = f"room_{next_id}"
        next_id += 1
        vault_room = Room(id=vault_id, name=vault_name, description=vault_description)
        vault_room.exits[OPPOSITE_DIRECTION[vault_direction]] = boss_id
        boss_room.exits[vault_direction] = vault_id
        rooms[vault_id] = vault_room
        coords[vault_id] = vault_coord
        room_at_coord[vault_coord] = vault_id
        vault_room.items = [Item(WIN_ITEM_NAME, crown_description)]
    else:
        # Every adjacent cell was occupied; fall back to the old behavior.
        vault_id = None
        boss_room.items = [Item(WIN_ITEM_NAME, crown_description)]

    other_ids = [
        room_id for room_id in rooms if room_id not in ("entrance", boss_id, vault_id)
    ]
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
            item_template = _pick_item_template(rng, player_class, upgrade_slot, upgrade_tier)
            room.items.append(item_from_template(item_template))

    return rooms
