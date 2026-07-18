from text_dungeon.minimap import compute_coords, render_map
from text_dungeon.models import Room


def _linear_rooms():
    return {
        "entrance": Room(
            id="entrance", name="Entrance", description="", exits={"north": "hallway"}
        ),
        "hallway": Room(id="hallway", name="Hallway", description="", exits={"south": "entrance"}),
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
