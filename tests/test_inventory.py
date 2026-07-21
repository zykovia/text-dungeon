from text_dungeon.inventory import (
    equip_item,
    equipped_line,
    inventory_lines,
    item_label,
    item_summary,
    take_item,
    unequip_item,
    use_item,
)
from text_dungeon.models import Item, Player, Room


def _player(player_class="Warrior", **kwargs) -> Player:
    return Player(name="Hero", player_class=player_class, **kwargs)


def test_take_item_moves_item_from_room_to_inventory():
    player = _player()
    room = Room(id="r1", name="Room", description="A room.")
    sword = Item("rusty sword", "A worn blade.", damage_bonus=2)
    room.items.append(sword)

    result = take_item(player, room, "rusty sword")

    assert result.item is sword
    assert result.blocked_by_class is False
    assert sword not in room.items
    assert sword in player.inventory


def test_take_item_blocks_wrong_class_and_leaves_it_in_room():
    player = _player(player_class="Warrior")
    room = Room(id="r1", name="Room", description="A room.")
    staff = Item("apprentice staff", "A wizard's staff.", player_class="Wizard")
    room.items.append(staff)

    result = take_item(player, room, "apprentice staff")

    assert result.blocked_by_class is True
    assert staff in room.items
    assert staff not in player.inventory


def test_take_item_missing_reports_not_found():
    player = _player()
    room = Room(id="r1", name="Room", description="A room.")

    result = take_item(player, room, "ghost")

    assert result.item is None
    assert result.blocked_by_class is False


def test_equip_item_retires_previous_occupant():
    player = _player()
    old = Item("rusty sword", "A worn blade.", slot="main_hand")
    new = Item("steel sword", "A sharper blade.", slot="main_hand")
    player.main_hand = old
    player.inventory.append(new)

    previous = equip_item(player, new)

    assert previous is old
    assert old.retired is True
    assert old in player.inventory
    assert player.main_hand is new
    assert new.retired is False
    assert new not in player.inventory


def test_equip_item_into_empty_slot_returns_none():
    player = _player()
    new = Item("wooden shield", "A shield.", slot="off_hand")
    player.inventory.append(new)

    previous = equip_item(player, new)

    assert previous is None
    assert player.off_hand is new


def test_unequip_item_moves_it_back_to_inventory():
    player = _player()
    sword = Item("rusty sword", "A worn blade.", slot="main_hand")
    player.main_hand = sword

    result = unequip_item(player, "rusty sword")

    assert result is sword
    assert player.main_hand is None
    assert sword in player.inventory


def test_unequip_item_not_equipped_returns_none():
    player = _player()

    assert unequip_item(player, "magic wand") is None


def test_use_item_heals_and_removes_from_inventory():
    player = _player(hp=5, max_hp=20)
    potion = Item("health potion", "Mends wounds.", heal=8)
    player.inventory.append(potion)

    result = use_item(player, "health potion")

    assert result.item is potion
    assert result.healed == 8
    assert player.hp == 13
    assert potion not in player.inventory


def test_use_item_heal_caps_at_max_hp():
    player = _player(hp=18, max_hp=20)
    potion = Item("health potion", "Mends wounds.", heal=8)
    player.inventory.append(potion)

    result = use_item(player, "health potion")

    assert result.healed == 2
    assert player.hp == 20


def test_use_item_without_heal_is_left_in_inventory():
    player = _player()
    sword = Item("rusty sword", "A worn blade.", damage_bonus=2)
    player.inventory.append(sword)

    result = use_item(player, "rusty sword")

    assert result.item is sword
    assert result.healed == 0
    assert sword in player.inventory


def test_use_item_missing_reports_not_found():
    player = _player()

    result = use_item(player, "ghost")

    assert result.item is None


def test_item_label_includes_effect_summary():
    sword = Item("rusty sword", "A worn blade.", damage_bonus=2)
    assert item_label(sword) == "rusty sword (+2 damage)"


def test_item_label_omits_parens_with_no_effect():
    trinket = Item("trinket", "A bauble.")
    assert item_label(trinket) == "trinket"


def test_equipped_line_formats_item_and_empty_slot():
    sword = Item("rusty sword", "A worn blade.", damage_bonus=2)
    assert equipped_line(sword) == "rusty sword (+2 damage): A worn blade."
    assert equipped_line(None) == "(empty)"


def test_item_summary_none_for_empty_slot():
    assert item_summary(None) is None


def test_item_summary_shape():
    sword = Item("rusty sword", "A worn blade.", damage_bonus=2)
    assert item_summary(sword) == {
        "name": "rusty sword",
        "description": "A worn blade.",
        "effect": "+2 damage",
    }


def test_inventory_lines_reports_empty_inventory():
    player = _player()

    lines = inventory_lines(player)

    assert lines[0] == "Main hand: (empty)"
    assert lines[1] == "Off hand: (empty)"
    assert lines[2] == "You aren't carrying anything else."


def test_inventory_lines_lists_active_items_and_collapses_retired():
    player = _player()
    potion = Item("health potion", "Mends wounds.", heal=8)
    old_sword = Item("rusty sword", "A worn blade.", damage_bonus=2, retired=True)
    player.inventory.extend([potion, old_sword])

    lines = inventory_lines(player)

    assert "- health potion (heals 8 HP): Mends wounds." in lines
    assert "- Old gear (1): rusty sword" in lines
    assert not any(line.startswith("- rusty sword") for line in lines)
