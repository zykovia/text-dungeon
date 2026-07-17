from text_dungeon.game import Game
from text_dungeon.world import build_world


def test_build_world_has_entrance():
    rooms = build_world()
    assert "entrance" in rooms
    assert rooms["entrance"].exits["north"] == "hallway"


def test_move_between_rooms():
    game = Game()
    assert game.player.current_room == "entrance"
    game.move("north")
    assert game.player.current_room == "hallway"


def test_move_blocked_by_monster():
    game = Game()
    game.move("north")
    game.move("east")  # crypt, guarded by a skeleton
    game.move("north")  # should be blocked
    assert game.player.current_room == "crypt"


def test_take_item_adds_to_inventory():
    game = Game()
    game.move("north")
    game.move("north")  # armory
    game.take("rusty sword")
    assert any(item.name == "rusty sword" for item in game.player.inventory)


def test_attack_damages_monster():
    game = Game()
    game.move("north")
    game.move("east")  # crypt, skeleton here
    monster = game.current_room().monster
    start_hp = monster.hp
    game.attack()
    assert monster.hp < start_hp


def test_use_potion_heals_player():
    game = Game()
    game.player.hp = 5
    game.move("north")
    game.move("east")  # crypt
    game.take("health potion")
    game.use("health potion")
    assert game.player.hp > 5
