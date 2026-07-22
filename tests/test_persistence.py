import json

from text_dungeon.character import create_player
from text_dungeon.game import Game
from text_dungeon.models import Item
from text_dungeon.persistence import (
    SAVE_VERSION,
    delete_save,
    load_player,
    load_summary,
    load_world,
    save_player,
    save_world,
)
from text_dungeon.world_state import World

WORLD_ID = "test-world"


def _player_path(save_dir, world_id, player_id):
    return save_dir / world_id / "players" / f"{player_id}.json"


def _world_path(save_dir, world_id):
    return save_dir / world_id / "world.json"


def test_load_player_with_no_save_returns_none(tmp_path):
    assert load_player(WORLD_ID, "nobody", save_dir=tmp_path) is None


def test_load_world_with_no_save_returns_none(tmp_path):
    assert load_world(WORLD_ID, save_dir=tmp_path) is None


def test_save_and_load_player_round_trips_state(tmp_path):
    game = Game(seed=1, player_class="Warrior")
    game.current_room().items.append(Item("bandage", "Rough cloth.", heal=4))
    game.take("bandage")
    game.move(next(iter(game.current_room().exits)))
    game.player.level = 3
    game.player.xp = 4
    game.player.hp = 11

    save_player(WORLD_ID, "player-1", game.player, game.running, save_dir=tmp_path)
    restored, running = load_player(WORLD_ID, "player-1", save_dir=tmp_path)

    assert running is True
    assert restored.level == 3
    assert restored.xp == 4
    assert restored.hp == 11
    assert restored.player_class == "Warrior"
    assert restored.current_room == game.player.current_room
    assert restored.visited == game.player.visited
    assert any(item.name == "bandage" for item in restored.inventory)


def test_save_and_load_player_round_trips_equipped_gear(tmp_path):
    game = Game(seed=1, player_class="Warrior")

    save_player(WORLD_ID, "player-1b", game.player, True, save_dir=tmp_path)
    restored, _ = load_player(WORLD_ID, "player-1b", save_dir=tmp_path)

    assert restored.main_hand.name == "rusty sword"
    assert restored.off_hand.name == "wooden shield"

    game.player = restored
    game.unequip("rusty sword")
    save_player(WORLD_ID, "player-1b", game.player, True, save_dir=tmp_path)
    restored_again, _ = load_player(WORLD_ID, "player-1b", save_dir=tmp_path)

    assert restored_again.main_hand is None
    assert any(item.name == "rusty sword" for item in restored_again.inventory)


def test_save_and_load_player_round_trips_skills_and_mana(tmp_path):
    game = Game(seed=1, player_class="Cleric")
    game.player.mana = 4
    game.player.pending_attack_buff = 3
    game.player.pending_block = True
    game.player.pending_monster_debuff = 2
    game.player.used_skills_this_round = {"heal"}

    save_player(WORLD_ID, "player-1c", game.player, True, save_dir=tmp_path)
    restored, _ = load_player(WORLD_ID, "player-1c", save_dir=tmp_path)

    assert restored.skills == ["heal"]
    assert restored.max_mana == 10
    assert restored.mana == 4
    assert restored.pending_attack_buff == 3
    assert restored.pending_block is True
    assert restored.pending_monster_debuff == 2
    assert restored.used_skills_this_round == {"heal"}


def test_save_and_load_world_round_trips_room_and_monster_state(tmp_path):
    game = Game(seed=1)
    room = game.current_room()
    monster = room.monster

    save_world(WORLD_ID, game.world, save_dir=tmp_path)
    restored = load_world(WORLD_ID, save_dir=tmp_path)

    restored_room = restored.levels[1][room.id]
    assert restored_room.name == room.name
    assert restored_room.exits == room.exits
    if monster is not None:
        assert restored_room.monster.name == monster.name
        assert restored_room.monster.hp == monster.hp


def test_save_and_load_world_round_trips_multiple_levels(tmp_path):
    world = World()
    level_1 = world.level_rooms(1, player_class=None, upgrade_slot=None, upgrade_tier=None, seed=1)
    level_2 = world.level_rooms(2, player_class=None, upgrade_slot=None, upgrade_tier=None, seed=2)

    save_world(WORLD_ID, world, save_dir=tmp_path)
    restored = load_world(WORLD_ID, save_dir=tmp_path)

    assert set(restored.levels) == {1, 2}
    assert set(restored.levels[1]) == set(level_1)
    assert set(restored.levels[2]) == set(level_2)


def test_delete_save_removes_only_the_player_file(tmp_path):
    game = Game(seed=1)
    save_world(WORLD_ID, game.world, save_dir=tmp_path)
    save_player(WORLD_ID, "player-3", game.player, True, save_dir=tmp_path)

    delete_save(WORLD_ID, "player-3", save_dir=tmp_path)

    assert load_player(WORLD_ID, "player-3", save_dir=tmp_path) is None
    assert load_world(WORLD_ID, save_dir=tmp_path) is not None


def test_save_and_load_player_round_trips_history_and_dungeon_marker(tmp_path):
    game = Game(seed=1)
    game.handle_command("look")
    direction, _ = next(iter(game.current_room().exits.items()))
    game.handle_command(f"go {direction}")

    save_player(WORLD_ID, "player-4", game.player, True, save_dir=tmp_path)
    restored, _ = load_player(WORLD_ID, "player-4", save_dir=tmp_path)

    assert restored.history == game.player.history
    assert restored.history[restored.dungeon_history_start :] == game.current_dungeon_history()


def test_load_player_rejects_a_save_from_a_different_version(tmp_path):
    game = Game(seed=1)
    save_player(WORLD_ID, "player-5", game.player, True, save_dir=tmp_path)
    path = _player_path(tmp_path, WORLD_ID, "player-5")
    state = json.loads(path.read_text())
    state["version"] = SAVE_VERSION - 1
    path.write_text(json.dumps(state))

    assert load_player(WORLD_ID, "player-5", save_dir=tmp_path) is None


def test_load_player_rejects_a_pre_versioning_save_missing_the_version_key(tmp_path):
    game = Game(seed=1)
    save_player(WORLD_ID, "player-6", game.player, True, save_dir=tmp_path)
    path = _player_path(tmp_path, WORLD_ID, "player-6")
    state = json.loads(path.read_text())
    del state["version"]
    path.write_text(json.dumps(state))

    assert load_player(WORLD_ID, "player-6", save_dir=tmp_path) is None


def test_load_player_deletes_an_incompatible_save_file(tmp_path):
    game = Game(seed=1)
    save_player(WORLD_ID, "player-7", game.player, True, save_dir=tmp_path)
    path = _player_path(tmp_path, WORLD_ID, "player-7")
    state = json.loads(path.read_text())
    state["version"] = SAVE_VERSION - 1
    path.write_text(json.dumps(state))

    load_player(WORLD_ID, "player-7", save_dir=tmp_path)

    assert not path.exists()


def test_load_world_deletes_an_incompatible_save_file(tmp_path):
    game = Game(seed=1)
    save_world(WORLD_ID, game.world, save_dir=tmp_path)
    path = _world_path(tmp_path, WORLD_ID)
    state = json.loads(path.read_text())
    state["version"] = SAVE_VERSION - 1
    path.write_text(json.dumps(state))

    load_world(WORLD_ID, save_dir=tmp_path)

    assert not path.exists()


def test_load_summary_with_no_save_returns_none(tmp_path):
    assert load_summary(WORLD_ID, "nobody", save_dir=tmp_path) is None


def test_load_summary_returns_none_and_keeps_the_file_on_version_mismatch(tmp_path):
    game = Game(seed=1, player_class="Warrior")
    save_player(WORLD_ID, "player-8", game.player, True, save_dir=tmp_path)
    path = _player_path(tmp_path, WORLD_ID, "player-8")
    state = json.loads(path.read_text())
    state["version"] = SAVE_VERSION - 1
    path.write_text(json.dumps(state))

    assert load_summary(WORLD_ID, "player-8", save_dir=tmp_path) is None
    assert path.exists()


def test_load_summary_reports_the_expected_fields(tmp_path):
    game = Game(seed=1, player_class="Warrior", player_name="Aria")
    game.player.level = 3
    game.player.xp = 4
    game.player.hp = 14
    game.player.dungeon_level = 2
    game.current_room().items.append(Item("bandage", "Rough cloth.", heal=4))
    game.take("bandage")
    save_player(WORLD_ID, "player-9", game.player, True, save_dir=tmp_path)

    summary = load_summary(WORLD_ID, "player-9", save_dir=tmp_path)

    assert summary["name"] == "Aria"
    assert summary["player_class"] == "Warrior"
    assert summary["level"] == 3
    assert summary["xp"] == 4
    assert summary["hp"] == 14
    assert summary["max_hp"] == game.player.max_hp
    assert summary["dungeon_level"] == 2
    assert summary["max_dungeon_level"] == 7
    # rusty sword + wooden shield (equipped) + bandage (inventory)
    assert summary["item_count"] == 3


def test_same_player_id_in_different_worlds_is_independent(tmp_path):
    player_a = create_player("Warrior")
    player_a.level = 5
    player_b = create_player("Wizard")
    player_b.level = 1

    save_player("world-a", "player-shared", player_a, True, save_dir=tmp_path)
    save_player("world-b", "player-shared", player_b, True, save_dir=tmp_path)

    restored_a, _ = load_player("world-a", "player-shared", save_dir=tmp_path)
    restored_b, _ = load_player("world-b", "player-shared", save_dir=tmp_path)
    assert restored_a.player_class == "Warrior"
    assert restored_a.level == 5
    assert restored_b.player_class == "Wizard"
    assert restored_b.level == 1

    delete_save("world-a", "player-shared", save_dir=tmp_path)
    assert load_player("world-a", "player-shared", save_dir=tmp_path) is None
    assert load_player("world-b", "player-shared", save_dir=tmp_path) is not None
