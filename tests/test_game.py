from text_dungeon.game import Game
from text_dungeon.models import Item, Monster


def test_move_between_rooms():
    game = Game(seed=1)
    direction, destination = next(iter(game.current_room().exits.items()))
    game.move(direction)
    assert game.player.current_room == destination


def test_move_blocked_by_monster():
    game = Game(seed=1)
    direction, _ = next(iter(game.current_room().exits.items()))
    game.current_room().monster = Monster("test monster", hp=5, attack=1)
    game.move(direction)
    assert game.player.current_room == "entrance"


def test_take_item_adds_to_inventory():
    game = Game(seed=1)
    game.current_room().items.append(Item("test item", "A thing.", damage_bonus=1))
    game.take("test item")
    assert any(item.name == "test item" for item in game.player.inventory)


def test_attack_damages_monster():
    game = Game(seed=1)
    game.current_room().monster = Monster("test monster", hp=20, attack=1)
    monster = game.current_room().monster
    start_hp = monster.hp
    game.attack()
    assert monster.hp < start_hp


def test_use_potion_heals_player():
    game = Game(seed=1)
    game.player.hp = 5
    game.current_room().items.append(
        Item("health potion", "A vial of red liquid that mends wounds.", heal=8)
    )
    game.take("health potion")
    game.use("health potion")
    assert game.player.hp > 5


def test_respawn_keeps_inventory_level_and_xp():
    game = Game(seed=1)
    game.current_room().items.append(Item("rusty sword", "A worn blade.", damage_bonus=2))
    game.take("rusty sword")
    game.player.level = 2
    game.player.max_hp = 25
    game.player.xp = 4

    game.player.hp = 0
    game.respawn(seed=2)

    assert any(item.name == "rusty sword" for item in game.player.inventory)
    assert game.player.level == 2
    assert game.player.xp == 4


def test_respawn_resets_position_hp_and_exploration():
    game = Game(seed=1)
    game.move(next(iter(game.current_room().exits)))
    game.player.hp = 0

    game.respawn(seed=2)

    assert game.player.current_room == "entrance"
    assert game.player.hp == game.player.max_hp
    assert game.player.visited == {"entrance"}


def test_dying_and_respawning_keeps_game_running():
    game = Game(seed=1)
    game.player.hp = 0
    assert not game.player.alive

    game.respawn(seed=2)

    assert game.running is True
    assert game.player.alive
