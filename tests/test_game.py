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
