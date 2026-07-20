import json

from text_dungeon.game import Game
from text_dungeon.models import Item
from text_dungeon.persistence import SAVE_VERSION, delete_save, load_game, save_game


def _save_path(save_dir, player_id):
    return save_dir / f"{player_id}.json"


def test_load_game_with_no_save_returns_none(tmp_path):
    assert load_game("nobody", save_dir=tmp_path) is None


def test_save_and_load_round_trips_player_state(tmp_path):
    game = Game(seed=1, player_class="Warrior")
    game.current_room().items.append(Item("bandage", "Rough cloth.", heal=4))
    game.take("bandage")
    game.move(next(iter(game.current_room().exits)))
    game.player.level = 3
    game.player.xp = 4
    game.player.hp = 11

    save_game("player-1", game, save_dir=tmp_path)
    restored = load_game("player-1", save_dir=tmp_path)

    assert restored.player.level == 3
    assert restored.player.xp == 4
    assert restored.player.hp == 11
    assert restored.player.player_class == "Warrior"
    assert restored.player.current_room == game.player.current_room
    assert restored.player.visited == game.player.visited
    assert any(item.name == "bandage" for item in restored.player.inventory)


def test_save_and_load_round_trips_equipped_gear(tmp_path):
    game = Game(seed=1, player_class="Warrior")

    save_game("player-1b", game, save_dir=tmp_path)
    restored = load_game("player-1b", save_dir=tmp_path)

    assert restored.player.main_hand.name == "rusty sword"
    assert restored.player.off_hand.name == "wooden shield"

    restored.unequip("rusty sword")
    save_game("player-1b", restored, save_dir=tmp_path)
    restored_again = load_game("player-1b", save_dir=tmp_path)

    assert restored_again.player.main_hand is None
    assert any(item.name == "rusty sword" for item in restored_again.player.inventory)


def test_save_and_load_round_trips_skills_and_mana(tmp_path):
    game = Game(seed=1, player_class="Cleric")
    game.player.mana = 4
    game.player.pending_attack_buff = 3
    game.player.pending_block = True
    game.player.pending_monster_debuff = 2

    save_game("player-1c", game, save_dir=tmp_path)
    restored = load_game("player-1c", save_dir=tmp_path)

    assert restored.player.skills == ["heal"]
    assert restored.player.max_mana == 10
    assert restored.player.mana == 4
    assert restored.player.pending_attack_buff == 3
    assert restored.player.pending_block is True
    assert restored.player.pending_monster_debuff == 2


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


def test_load_game_rejects_a_save_from_a_different_version(tmp_path):
    game = Game(seed=1)
    save_game("player-5", game, save_dir=tmp_path)
    path = _save_path(tmp_path, "player-5")
    state = json.loads(path.read_text())
    state["version"] = SAVE_VERSION - 1
    path.write_text(json.dumps(state))

    assert load_game("player-5", save_dir=tmp_path) is None


def test_load_game_rejects_a_pre_versioning_save_missing_the_version_key(tmp_path):
    game = Game(seed=1)
    save_game("player-6", game, save_dir=tmp_path)
    path = _save_path(tmp_path, "player-6")
    state = json.loads(path.read_text())
    del state["version"]
    path.write_text(json.dumps(state))

    assert load_game("player-6", save_dir=tmp_path) is None


def test_load_game_deletes_an_incompatible_save_file(tmp_path):
    game = Game(seed=1)
    save_game("player-7", game, save_dir=tmp_path)
    path = _save_path(tmp_path, "player-7")
    state = json.loads(path.read_text())
    state["version"] = SAVE_VERSION - 1
    path.write_text(json.dumps(state))

    load_game("player-7", save_dir=tmp_path)

    assert not path.exists()
