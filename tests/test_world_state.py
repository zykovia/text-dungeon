from text_dungeon.world_state import World


def _rooms(world, level, seed=1, player_class=None):
    return world.level_rooms(
        level, player_class=player_class, upgrade_slot=None, upgrade_tier=None, seed=seed
    )


def test_level_rooms_generates_once_and_caches():
    world = World()

    first = _rooms(world, 1)
    second = _rooms(world, 1)

    assert first is second


def test_level_rooms_gives_different_levels_independent_room_sets():
    world = World()

    level_1 = _rooms(world, 1, seed=1)
    level_2 = _rooms(world, 2, seed=1)

    assert level_1 is not level_2
    assert set(level_1) != set(level_2) or level_1 is not level_2


def test_level_rooms_ignores_new_bias_once_a_level_already_exists():
    world = World()

    first = _rooms(world, 1, seed=1, player_class="Warrior")
    second = _rooms(world, 1, seed=1, player_class="Wizard")

    assert first is second


def test_level_rooms_is_deterministic_for_a_given_seed():
    world_a = World()
    world_b = World()

    rooms_a = _rooms(world_a, 1, seed=42)
    rooms_b = _rooms(world_b, 1, seed=42)

    assert set(rooms_a) == set(rooms_b)
    for room_id in rooms_a:
        assert rooms_a[room_id].name == rooms_b[room_id].name
        assert rooms_a[room_id].exits == rooms_b[room_id].exits
