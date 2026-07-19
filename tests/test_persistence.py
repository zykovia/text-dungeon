from text_dungeon.game import Game
from text_dungeon.models import Item
from text_dungeon.persistence import delete_save, load_game, save_game


def test_load_game_with_no_save_returns_none(tmp_path):
    assert load_game("nobody", save_dir=tmp_path) is None


def test_save_and_load_round_trips_player_state(tmp_path):
    game = Game(seed=1)
    game.current_room().items.append(Item("rusty sword", "A worn blade.", damage_bonus=2))
    game.take("rusty sword")
    game.move(next(iter(game.current_room().exits)))
    game.player.level = 3
    game.player.xp = 4
    game.player.hp = 11

    save_game("player-1", game, save_dir=tmp_path)
    restored = load_game("player-1", save_dir=tmp_path)

    assert restored.player.level == 3
    assert restored.player.xp == 4
    assert restored.player.hp == 11
    assert restored.player.current_room == game.player.current_room
    assert restored.player.visited == game.player.visited
    assert any(item.name == "rusty sword" for item in restored.player.inventory)


def test_save_and_load_round_trips_room_and_monster_state(tmp_path):
    game = Game(seed=1)
    room = game.current_room()
    monster = room.monster

    save_game("player-2", game, save_dir=tmp_path)
    restored = load_game("player-2", save_dir=tmp_path)

    restored_room = restored.rooms[room.id]
    assert restored_room.name == room.name
    assert restored_room.exits == room.exits
    if monster is not None:
        assert restored_room.monster.name == monster.name
        assert restored_room.monster.hp == monster.hp
    assert restored.running is True


def test_delete_save_removes_the_saved_game(tmp_path):
    game = Game(seed=1)
    save_game("player-3", game, save_dir=tmp_path)

    delete_save("player-3", save_dir=tmp_path)

    assert load_game("player-3", save_dir=tmp_path) is None


def test_save_and_load_round_trips_history_and_dungeon_marker(tmp_path):
    game = Game(seed=1)
    game.handle_command("look")
    direction, _ = next(iter(game.current_room().exits.items()))
    game.handle_command(f"go {direction}")

    save_game("player-4", game, save_dir=tmp_path)
    restored = load_game("player-4", save_dir=tmp_path)

    assert restored.player.history == game.player.history
    assert restored.current_dungeon_history() == game.current_dungeon_history()
