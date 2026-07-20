from text_dungeon.combat import resolve_attack
from text_dungeon.models import Item, Monster, Player


def test_resolve_attack_damages_monster():
    player = Player(name="Hero", player_class="Warrior")
    monster = Monster("goblin", hp=20, attack=1)
    result = resolve_attack(player, monster)
    assert result.damage_dealt > 0
    assert monster.hp == 20 - result.damage_dealt


def test_resolve_attack_applies_weapon_bonus():
    player = Player(name="Hero", player_class="Warrior")
    player.inventory.append(Item("sword", "A blade.", damage_bonus=100))
    monster = Monster("goblin", hp=1000, attack=0)
    result = resolve_attack(player, monster)
    assert result.damage_dealt >= 100


def test_resolve_attack_defeats_monster_without_retaliation():
    player = Player(name="Hero", player_class="Warrior")
    monster = Monster("goblin", hp=1, attack=50)
    result = resolve_attack(player, monster)
    assert result.monster_defeated is True
    assert result.incoming_damage == 0
    assert player.hp == player.max_hp


def test_resolve_attack_survivor_retaliates():
    player = Player(name="Hero", player_class="Warrior", attack=0)
    monster = Monster("goblin", hp=1000, attack=5)
    start_hp = player.hp
    result = resolve_attack(player, monster)
    assert result.monster_defeated is False
    assert result.incoming_damage > 0
    assert player.hp < start_hp
