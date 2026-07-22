from text_dungeon.character import create_player
from text_dungeon.game import Game
from text_dungeon.models import Room
from text_dungeon.web.server import _accumulate, _player_ids_who_know_room, _status_with_players
from text_dungeon.world_state import World


def _chain_world():
    """entrance -> hallway -> vault, all on level 1 of a shared World."""
    rooms = {
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
    return World(levels={1: rooms})


def _game_at(world, dungeon_level, room_id, name="P", player_class="Warrior"):
    player = create_player(player_class, name=name)
    player.dungeon_level = dungeon_level
    game = Game(player=player, world=world)
    game.look()  # populate visited for the starting room
    game.player.current_room = room_id
    if dungeon_level == 1:
        game.look()  # re-populate visited for the actual target room too
    return game


def test_player_ids_who_know_room_matches_same_room():
    world = _chain_world()
    acting = _game_at(world, 1, "entrance", name="Acting")
    same_room = _game_at(world, 1, "entrance", name="SameRoom")
    sessions = {"acting": (None, acting), "same-room": (None, same_room)}

    matches = _player_ids_who_know_room(sessions, 1, "entrance", exclude_player_id="acting")

    assert matches == ["same-room"]


def test_player_ids_who_know_room_matches_a_visible_neighbor():
    world = _chain_world()
    acting = _game_at(world, 1, "entrance", name="Acting")
    neighbor_viewer = _game_at(world, 1, "entrance", name="Neighbor")  # sees hallway too
    sessions = {"acting": (None, acting), "neighbor": (None, neighbor_viewer)}

    # The event happened in "hallway" - a neighbor of entrance, which
    # neighbor_viewer can see even without having visited it.
    matches = _player_ids_who_know_room(sessions, 1, "hallway", exclude_player_id="acting")

    assert matches == ["neighbor"]


def test_player_ids_who_know_room_excludes_a_session_that_cannot_see_the_room():
    world = _chain_world()
    acting = _game_at(world, 1, "vault", name="Acting")
    far_viewer = _game_at(world, 1, "entrance", name="Far")  # can't see "vault" from entrance
    sessions = {"acting": (None, acting), "far": (None, far_viewer)}

    matches = _player_ids_who_know_room(sessions, 1, "vault", exclude_player_id="acting")

    assert matches == []


def test_player_ids_who_know_room_does_not_cross_levels_even_with_the_same_room_id():
    world = World()
    level_1_rooms = world.level_rooms(
        1, player_class=None, upgrade_slot=None, upgrade_tier=None, seed=1
    )
    assert "room_1" in level_1_rooms  # sanity
    world.level_rooms(2, player_class=None, upgrade_slot=None, upgrade_tier=None, seed=2)

    acting_player = create_player("Warrior", name="Acting")
    acting_player.dungeon_level = 1
    acting = Game(player=acting_player, world=world)
    acting.player.current_room = "room_1"

    other_player = create_player("Ranger", name="Other")
    other_player.dungeon_level = 2
    other = Game(player=other_player, world=world)
    other.look()
    other.player.current_room = "room_1"
    other.look()  # "room_1" on level 2 is now visited/known for `other`

    sessions = {"acting": (None, acting), "other": (None, other)}

    matches = _player_ids_who_know_room(sessions, 1, "room_1", exclude_player_id="acting")

    assert matches == []


def test_player_ids_who_know_room_excludes_the_acting_player_even_if_matching():
    world = _chain_world()
    acting = _game_at(world, 1, "entrance", name="Acting")
    sessions = {"acting": (None, acting)}

    matches = _player_ids_who_know_room(sessions, 1, "entrance", exclude_player_id="acting")

    assert matches == []


def test_player_ids_who_know_room_returns_empty_for_no_sessions():
    assert _player_ids_who_know_room({}, 1, "entrance", exclude_player_id="acting") == []


def test_status_with_players_lists_others_in_the_same_room_and_excludes_self():
    world = _chain_world()
    viewer = _game_at(world, 1, "entrance", name="Viewer")
    other_here = _game_at(world, 1, "entrance", name="Other")
    sessions = {"viewer": (None, viewer), "other": (None, other_here)}

    status = _status_with_players(viewer, sessions, exclude_player_id="viewer")

    assert status["rooms"]["entrance"]["players"] == [
        {"name": "Other", "player_class": "Warrior"}
    ]


def test_status_with_players_excludes_the_requested_player_from_their_own_room():
    world = _chain_world()
    viewer = _game_at(world, 1, "entrance", name="Viewer")
    sessions = {"viewer": (None, viewer)}

    status = _status_with_players(viewer, sessions, exclude_player_id="viewer")

    assert status["rooms"]["entrance"]["players"] == []


def test_accumulate_merges_multiple_calls_for_the_same_recipient():
    world = _chain_world()
    acting = _game_at(world, 1, "entrance", name="Acting")
    viewer = _game_at(world, 1, "entrance", name="Viewer")
    sessions = {"acting": (None, acting), "viewer": (None, viewer)}

    pending: dict[str, list[str]] = {}
    _accumulate(pending, sessions, 1, "entrance", exclude_player_id="acting", message="First thing.")
    _accumulate(pending, sessions, 1, "entrance", exclude_player_id="acting")  # silent presence event

    assert pending == {"viewer": ["First thing."]}


def test_accumulate_adds_a_recipient_with_no_message_for_a_silent_event():
    world = _chain_world()
    acting = _game_at(world, 1, "entrance", name="Acting")
    viewer = _game_at(world, 1, "entrance", name="Viewer")
    sessions = {"acting": (None, acting), "viewer": (None, viewer)}

    pending: dict[str, list[str]] = {}
    _accumulate(pending, sessions, 1, "entrance", exclude_player_id="acting")

    assert pending == {"viewer": []}
