from collections import deque

from text_dungeon.directions import OPPOSITE_DIRECTION
from text_dungeon.game import Game
from text_dungeon.models import Item, Monster
from text_dungeon.world import generate_dungeon


def test_generate_dungeon_all_rooms_reachable_from_entrance():
    rooms = generate_dungeon(seed=42)
    reachable = {"entrance"}
    queue = deque(["entrance"])
    while queue:
        room_id = queue.popleft()
        for dest in rooms[room_id].exits.values():
            if dest not in reachable:
                reachable.add(dest)
                queue.append(dest)
    assert reachable == set(rooms)


def test_generate_dungeon_exits_are_reciprocal():
    rooms = generate_dungeon(seed=3)
    for room_id, room in rooms.items():
        for direction, dest in room.exits.items():
            assert rooms[dest].exits.get(OPPOSITE_DIRECTION[direction]) == room_id


def test_generate_dungeon_has_exactly_one_win_condition():
    rooms = generate_dungeon(seed=42)
    boss_rooms = [room for room in rooms.values() if any(item.name == "golden crown" for item in room.items)]
    assert len(boss_rooms) == 1
    assert boss_rooms[0].monster is not None
    assert boss_rooms[0].monster.name == "Dungeon Lord"


def test_generate_dungeon_seed_is_reproducible():
    rooms_a = generate_dungeon(seed=7)
    rooms_b = generate_dungeon(seed=7)
    assert {room_id: room.exits for room_id, room in rooms_a.items()} == {
        room_id: room.exits for room_id, room in rooms_b.items()
    }


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
