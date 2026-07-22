from text_dungeon.character import create_player
from text_dungeon.game import Game
from text_dungeon.web.server import _player_ids_in_room
from text_dungeon.world_state import World


def _game_in_room(dungeon_level, room_id):
    world = World()
    player = create_player("Warrior")
    game = Game(player=player, world=world)
    game.player.dungeon_level = dungeon_level
    game.player.current_room = room_id
    return game


def test_player_ids_in_room_matches_same_level_and_room():
    sessions = {
        "acting": (None, _game_in_room(1, "entrance")),
        "same-room": (None, _game_in_room(1, "entrance")),
        "other-room": (None, _game_in_room(1, "room_1")),
        "other-level": (None, _game_in_room(2, "entrance")),
    }

    matches = _player_ids_in_room(sessions, 1, "entrance", exclude_player_id="acting")

    assert matches == ["same-room"]


def test_player_ids_in_room_excludes_the_acting_player_even_if_matching():
    sessions = {"acting": (None, _game_in_room(1, "entrance"))}

    matches = _player_ids_in_room(sessions, 1, "entrance", exclude_player_id="acting")

    assert matches == []


def test_player_ids_in_room_returns_empty_for_no_sessions():
    assert _player_ids_in_room({}, 1, "entrance", exclude_player_id="acting") == []
