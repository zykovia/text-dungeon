import pytest

from text_dungeon.character import create_player
from text_dungeon.templates import CLASS_TEMPLATES


@pytest.mark.parametrize("template", CLASS_TEMPLATES, ids=lambda t: t.name)
def test_create_player_applies_class_starting_stats_and_gear(template):
    player = create_player(template.name)

    assert player.player_class == template.name
    assert player.hp == template.starting_hp
    assert player.max_hp == template.starting_hp
    assert player.attack == template.starting_attack
    assert len(player.inventory) == 1
    assert player.inventory[0].name == template.starting_item


def test_create_player_uses_given_name():
    player = create_player("Warrior", name="Grog")
    assert player.name == "Grog"


def test_create_player_rejects_unknown_class():
    with pytest.raises(ValueError):
        create_player("Necromancer")
