from text_dungeon.balance import MAX_DUNGEON_LEVEL
from text_dungeon.game import Game
from text_dungeon.models import Item, Monster
from text_dungeon.world import room_count_range


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


def test_taking_the_crown_advances_to_a_new_larger_dungeon():
    game = Game(seed=1)
    game.player.level = 2
    game.player.xp = 3
    game.current_room().items.append(Item("rusty sword", "A worn blade.", damage_bonus=2))
    game.take("rusty sword")

    game.current_room().items.append(Item("golden crown", "The Dungeon Lord's crown."))
    game.take("golden crown")

    assert game.player.dungeon_level == 2
    assert game.player.level == 2
    assert game.player.xp == 3
    assert any(item.name == "rusty sword" for item in game.player.inventory)
    assert any(item.name == "golden crown" for item in game.player.inventory)
    assert game.player.current_room == "entrance"
    assert game.running is True


def test_advancing_generates_a_dungeon_sized_for_the_new_level():
    game = Game(seed=1)
    game.player.dungeon_level = 3

    game.advance(seed=5)

    assert game.player.dungeon_level == 4
    min_rooms, max_rooms = room_count_range(4)
    # +1 to account for the crown's vault room, attached beyond the boss chamber.
    assert min_rooms <= len(game.rooms) <= max_rooms + 1


def test_taking_the_crown_at_max_dungeon_level_ends_the_game():
    game = Game(seed=1)
    game.player.dungeon_level = MAX_DUNGEON_LEVEL
    game.current_room().items.append(Item("golden crown", "The Dungeon Emperor's crown."))

    game.take("golden crown")

    assert game.running is False
    assert game.player.dungeon_level == MAX_DUNGEON_LEVEL


def test_taking_the_crown_below_max_dungeon_level_advances():
    game = Game(seed=1)
    game.player.dungeon_level = MAX_DUNGEON_LEVEL - 1
    game.current_room().items.append(Item("golden crown", "The Dungeon Lord's crown."))

    game.take("golden crown")

    assert game.running is True
    assert game.player.dungeon_level == MAX_DUNGEON_LEVEL


def test_history_records_moves_looks_and_attacks():
    game = Game(seed=1)
    game.current_room().monster = Monster("test monster", hp=5, attack=1)
    direction, _ = next(iter(game.current_room().exits.items()))

    game.handle_command("look")
    game.attack()
    game.handle_command(f"go {direction}")

    history_text = "\n".join(game.player.history)
    assert "test monster" in history_text
    assert "strike" in history_text
    assert "Exits" in history_text


def test_advancing_starts_a_fresh_current_dungeon_history():
    game = Game(seed=1)
    game.handle_command("look")
    assert len(game.current_dungeon_history()) > 0

    game.advance(seed=5)

    new_dungeon_history = game.current_dungeon_history()
    assert new_dungeon_history[0] == (
        f"A new dungeon awaits below, larger than the last (depth {game.player.dungeon_level})."
    )


def test_show_history_does_not_duplicate_itself_on_repeat_calls():
    game = Game(seed=1)
    game.handle_command("look")
    before = list(game.player.history)

    game.show_history()
    game.pop_output()

    assert game.player.history == before


def test_take_blocked_for_wrong_class_item_stays_in_room():
    game = Game(seed=1, player_class="Warrior")
    game.current_room().items.append(
        Item("apprentice staff", "A gnarled staff.", damage_bonus=3, player_class="Wizard")
    )

    game.take("apprentice staff")

    assert not any(item.name == "apprentice staff" for item in game.player.inventory)
    assert any(item.name == "apprentice staff" for item in game.current_room().items)
    assert "Only a Wizard can wield the apprentice staff." in game.pop_output()


def test_take_allowed_for_matching_class_item():
    game = Game(seed=1, player_class="Wizard")
    game.current_room().items.append(
        Item("apprentice staff", "A gnarled staff.", damage_bonus=3, player_class="Wizard")
    )

    game.take("apprentice staff")

    assert any(item.name == "apprentice staff" for item in game.player.inventory)
    assert not any(item.name == "apprentice staff" for item in game.current_room().items)


def test_take_allowed_for_class_agnostic_item():
    game = Game(seed=1, player_class="Cleric")
    game.current_room().items.append(Item("health potion", "Mends wounds.", heal=8))

    game.take("health potion")

    assert any(item.name == "health potion" for item in game.player.inventory)


def test_class_determines_starting_stats_and_gear():
    game = Game(player_class="Wizard")

    assert game.player.player_class == "Wizard"
    assert game.player.hp == game.player.max_hp == 16
    assert game.player.attack == 2
    assert game.player.main_hand.name == "apprentice staff"
    assert game.player.off_hand.name == "spellbook"


def test_class_with_no_name_falls_back_to_the_class_default_name():
    game = Game(player_class="Wizard")

    assert game.player.name == "Yennefer"
    assert game.status()["name"] == "Yennefer"


def test_player_name_can_be_chosen():
    game = Game(player_class="Wizard", player_name="Gandalf")

    assert game.player.name == "Gandalf"
    assert game.status()["name"] == "Gandalf"


def test_equip_swaps_into_occupied_slot_and_returns_old_item_to_inventory():
    game = Game(seed=1, player_class="Warrior")
    old_weapon = game.player.main_hand
    new_weapon = Item(
        "steel sword", "A sharper blade.", damage_bonus=4, player_class="Warrior", slot="main_hand"
    )
    game.player.inventory.append(new_weapon)

    game.equip("steel sword")

    assert game.player.main_hand is new_weapon
    assert old_weapon in game.player.inventory
    assert new_weapon not in game.player.inventory


def test_equip_refuses_non_equippable_item():
    game = Game(seed=1, player_class="Warrior")
    game.player.inventory.append(Item("health potion", "Mends wounds.", heal=8))

    game.equip("health potion")

    assert game.player.main_hand.name != "health potion"
    assert any(item.name == "health potion" for item in game.player.inventory)
    assert "You can't equip the health potion." in game.pop_output()


def test_equip_already_equipped_item_is_a_no_op():
    game = Game(seed=1, player_class="Warrior")

    game.equip("rusty sword")

    assert game.player.main_hand.name == "rusty sword"
    assert "You already have the rusty sword equipped." in game.pop_output()


def test_equip_missing_item_reports_not_carried():
    game = Game(seed=1, player_class="Warrior")

    game.equip("magic wand")

    assert "You don't have a 'magic wand'." in game.pop_output()


def test_unequip_moves_item_back_to_inventory():
    game = Game(seed=1, player_class="Warrior")

    game.unequip("rusty sword")

    assert game.player.main_hand is None
    assert any(item.name == "rusty sword" for item in game.player.inventory)


def test_unequip_not_equipped_reports_distinct_message():
    game = Game(seed=1, player_class="Warrior")

    game.unequip("magic wand")

    assert "You don't have 'magic wand' equipped." in game.pop_output()


def test_status_includes_equipment():
    game = Game(seed=1, player_class="Warrior")

    equipment = game.status()["equipment"]

    assert equipment["main_hand"]["name"] == "rusty sword"
    assert equipment["off_hand"]["name"] == "wooden shield"
