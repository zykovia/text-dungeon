from collections import deque

from text_dungeon.balance import MAX_DUNGEON_LEVEL
from text_dungeon.directions import DIRECTION_DELTAS, OPPOSITE_DIRECTION
from text_dungeon.minimap import compute_coords
from text_dungeon.templates import BOSS, ITEM_TEMPLATES, SUPER_BOSS
from text_dungeon.world import generate_dungeon, is_final_dungeon, room_count_range


def _crown_rooms(rooms):
    return [
        room for room in rooms.values() if any(item.name == "golden crown" for item in room.items)
    ]


_BOSS_MONSTER_NAMES = {BOSS.monster_name, SUPER_BOSS.monster_name}


def _boss_monster_room(rooms):
    return next(
        room
        for room in rooms.values()
        if room.monster is not None and room.monster.name in _BOSS_MONSTER_NAMES
    )


def test_generate_dungeon_all_rooms_reachable_from_entrance():
    rooms = generate_dungeon(seed=42)
    reachable = {"entrance"}
    queue = deque(["entrance"])
    while queue:
        room_id = queue.popleft()
        for dest in rooms[room_id].exits.values():
            if dest not in reachable:
                reachable.add(dest)
                queue.append(dest)
    assert reachable == set(rooms)


def test_generate_dungeon_exits_are_reciprocal():
    rooms = generate_dungeon(seed=3)
    for room_id, room in rooms.items():
        for direction, dest in room.exits.items():
            assert rooms[dest].exits.get(OPPOSITE_DIRECTION[direction]) == room_id


def test_generate_dungeon_has_exactly_one_win_condition():
    rooms = generate_dungeon(seed=42)
    crown_rooms = _crown_rooms(rooms)
    assert len(crown_rooms) == 1
    boss_room = _boss_monster_room(rooms)
    assert boss_room.monster.name == "Dungeon Lord"


def test_generate_dungeon_crown_room_is_guarded_by_the_boss():
    # The crown must sit behind the boss, not alongside it, so a player can't
    # grab it and skip the fight: it lives alone in a vault whose only exit
    # leads back to the room holding the boss monster.
    for seed in range(20):
        rooms = generate_dungeon(seed=seed)
        crown_room = _crown_rooms(rooms)[0]
        assert crown_room.monster is None
        assert len(crown_room.items) == 1
        assert len(crown_room.exits) == 1
        boss_id = next(iter(crown_room.exits.values()))
        assert rooms[boss_id].monster is not None


def test_generate_dungeon_seed_is_reproducible():
    rooms_a = generate_dungeon(seed=7)
    rooms_b = generate_dungeon(seed=7)
    assert {room_id: room.exits for room_id, room in rooms_a.items()} == {
        room_id: room.exits for room_id, room in rooms_b.items()
    }


def test_generate_dungeon_handles_rooms_beyond_the_template_pool():
    # 15 rooms needs 14 room templates, more than the 10 available; must not crash.
    # +1 possible for the crown's vault room, attached beyond the boss chamber.
    rooms = generate_dungeon(seed=1, min_rooms=15, max_rooms=15)
    assert len(rooms) in (15, 16)


def test_room_count_range_grows_with_dungeon_level():
    assert room_count_range(1) == (6, 10)
    assert room_count_range(2) == (8, 12)
    assert room_count_range(3) == (10, 14)


def test_is_final_dungeon_at_and_beyond_max_level():
    assert is_final_dungeon(MAX_DUNGEON_LEVEL - 1) is False
    assert is_final_dungeon(MAX_DUNGEON_LEVEL) is True
    assert is_final_dungeon(MAX_DUNGEON_LEVEL + 1) is True


def test_generate_dungeon_places_regular_boss_by_default():
    rooms = generate_dungeon(seed=42)
    assert _boss_monster_room(rooms).monster.name == BOSS.monster_name


def test_generate_dungeon_places_super_boss_when_final():
    rooms = generate_dungeon(seed=42, final_boss=True)
    assert _boss_monster_room(rooms).monster.name == SUPER_BOSS.monster_name


def test_generate_dungeon_spawned_items_keep_their_class_restriction():
    # A randomly-spawned "rusty sword" etc. must stay Warrior-only; dropping
    # player_class here would let any class pick up and wield class gear.
    class_restricted = {t.name: t.player_class for t in ITEM_TEMPLATES if t.player_class}
    checked_any = False
    for seed in range(50):
        rooms = generate_dungeon(seed=seed, min_rooms=18, max_rooms=22)
        for room in rooms.values():
            for item in room.items:
                if item.name in class_restricted:
                    checked_any = True
                    assert item.player_class == class_restricted[item.name]
    assert checked_any


def test_generate_dungeon_never_places_unconnected_rooms_adjacent():
    # Two rooms sharing a grid edge must be linked by an exit; otherwise the
    # minimap would draw them touching even though there's no way to walk
    # between them.
    for seed in range(50):
        rooms = generate_dungeon(seed=seed, min_rooms=18, max_rooms=22)
        coords = compute_coords(rooms)
        room_at_coord = {coord: room_id for room_id, coord in coords.items()}
        for room_id, room in rooms.items():
            x, y = coords[room_id]
            for direction, (dx, dy) in DIRECTION_DELTAS.items():
                neighbor_id = room_at_coord.get((x + dx, y + dy))
                if neighbor_id is not None:
                    assert room.exits.get(direction) == neighbor_id
