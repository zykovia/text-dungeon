from text_dungeon.minimap import compute_coords, known_room_ids, render_map, room_snapshots
from text_dungeon.models import Item, Monster, Room


def _linear_rooms():
    return {
        "entrance": Room(
            id="entrance", name="Entrance", description="", exits={"north": "hallway"}
        ),
        "hallway": Room(id="hallway", name="Hallway", description="", exits={"south": "entrance"}),
    }


def _chain_rooms():
    """entrance -> hallway -> vault, so hallway has a neighbor beyond it."""
    return {
        "entrance": Room(
            id="entrance", name="Entrance", description="", exits={"north": "hallway"}
        ),
        "hallway": Room(
            id="hallway",
            name="Hallway",
            description="",
            exits={"south": "entrance", "north": "vault"},
        ),
        "vault": Room(id="vault", name="Vault", description="", exits={"south": "hallway"}),
    }


def test_compute_coords_places_entrance_at_origin():
    coords = compute_coords(_linear_rooms())
    assert coords["entrance"] == (0, 0)
    assert coords["hallway"] == (0, 1)


def test_render_map_shows_no_exploration_message_when_unvisited():
    rooms = _linear_rooms()
    coords = compute_coords(rooms)
    lines = render_map(rooms, coords, visited=set(), current_room="entrance")
    assert lines == ["You haven't explored anywhere yet."]


def test_render_map_marks_current_room_and_fog_of_war():
    rooms = _linear_rooms()
    coords = compute_coords(rooms)
    lines = render_map(rooms, coords, visited={"entrance"}, current_room="entrance")
    joined = "\n".join(lines)
    assert "[@]" in joined
    assert "[?]" in joined
    assert "[#]" not in joined


def test_known_room_ids_is_visited_plus_immediate_neighbors():
    rooms = _chain_rooms()

    known = known_room_ids(rooms, visited={"entrance"})

    assert known == {"entrance", "hallway"}
    assert "vault" not in known


def test_room_snapshots_scoped_to_visited_and_their_neighbors():
    rooms = _chain_rooms()
    coords = compute_coords(rooms)

    snapshots = room_snapshots(rooms, coords, visited={"entrance"}, current_room="entrance")

    assert set(snapshots) == {"entrance", "hallway"}
    assert "vault" not in snapshots


def test_room_snapshots_after_moving_reveals_the_next_neighbor():
    rooms = _chain_rooms()
    coords = compute_coords(rooms)

    snapshots = room_snapshots(
        rooms, coords, visited={"entrance", "hallway"}, current_room="hallway"
    )

    assert set(snapshots) == {"entrance", "hallway", "vault"}
    assert snapshots["hallway"]["current"] is True
    assert snapshots["hallway"]["visited"] is True
    assert snapshots["entrance"]["current"] is False
    assert snapshots["vault"]["visited"] is False


def test_room_snapshots_coordinates_match_compute_coords():
    rooms = _chain_rooms()
    coords = compute_coords(rooms)

    snapshots = room_snapshots(rooms, coords, visited={"entrance"}, current_room="entrance")

    for room_id, snapshot in snapshots.items():
        assert (snapshot["x"], snapshot["y"]) == coords[room_id]


def test_room_snapshots_hides_a_defeated_monster():
    rooms = _linear_rooms()
    rooms["entrance"].monster = Monster("rat", hp=0, attack=1)
    coords = compute_coords(rooms)

    snapshots = room_snapshots(rooms, coords, visited={"entrance"}, current_room="entrance")

    assert snapshots["entrance"]["monster"] is None


def test_room_snapshots_reports_a_living_monster():
    rooms = _linear_rooms()
    rooms["entrance"].monster = Monster("rat", hp=5, attack=1)
    coords = compute_coords(rooms)

    snapshots = room_snapshots(rooms, coords, visited={"entrance"}, current_room="entrance")

    assert snapshots["entrance"]["monster"] == "rat"


def test_room_snapshots_lists_item_names():
    rooms = _linear_rooms()
    rooms["entrance"].items.append(Item("bandage", "Rough cloth."))
    coords = compute_coords(rooms)

    snapshots = room_snapshots(rooms, coords, visited={"entrance"}, current_room="entrance")

    assert snapshots["entrance"]["items"] == ["bandage"]


def test_room_snapshots_auto_advance_can_coexist_with_a_live_monster():
    """The boss-room fallback (world.py) sets auto_advance on a room that also has a boss."""
    rooms = _linear_rooms()
    rooms["entrance"].monster = Monster("Dungeon Lord", hp=20, attack=5)
    rooms["entrance"].auto_advance = True
    coords = compute_coords(rooms)

    snapshots = room_snapshots(rooms, coords, visited={"entrance"}, current_room="entrance")

    assert snapshots["entrance"]["auto_advance"] is True
    assert snapshots["entrance"]["monster"] == "Dungeon Lord"
