from text_dungeon.leveling import (
    BOSS_XP,
    MONSTER_XP,
    SUPER_BOSS_XP,
    XP_PER_LEVEL,
    gain_xp,
    xp_for_kill,
)
from text_dungeon.models import Player


def test_xp_for_kill_regular_monster():
    assert xp_for_kill("skeleton", boss_name="Dungeon Lord") == MONSTER_XP


def test_xp_for_kill_boss():
    assert xp_for_kill("Dungeon Lord", boss_name="Dungeon Lord") == BOSS_XP


def test_xp_for_kill_super_boss():
    assert (
        xp_for_kill("Dungeon Emperor", boss_name="Dungeon Lord", super_boss_name="Dungeon Emperor")
        == SUPER_BOSS_XP
    )


def test_xp_for_kill_regular_boss_when_super_boss_name_also_given():
    assert (
        xp_for_kill("Dungeon Lord", boss_name="Dungeon Lord", super_boss_name="Dungeon Emperor")
        == BOSS_XP
    )


def test_gain_xp_below_threshold_no_level_up():
    player = Player(name="Hero", player_class="Warrior")
    level_ups = gain_xp(player, XP_PER_LEVEL - 1)
    assert level_ups == []
    assert player.level == 1
    assert player.xp == XP_PER_LEVEL - 1


def test_gain_xp_triggers_level_up_and_heals():
    player = Player(name="Hero", player_class="Warrior")
    player.hp = 1
    level_ups = gain_xp(player, XP_PER_LEVEL)
    assert len(level_ups) == 1
    assert player.level == 2
    assert player.max_hp == 25
    assert player.hp == player.max_hp
    assert player.xp == 0


def test_gain_xp_overflow_carries_remainder_and_can_multi_level():
    player = Player(name="Hero", player_class="Warrior")
    level_ups = gain_xp(player, XP_PER_LEVEL * 2 + 3)
    assert [level_up.level for level_up in level_ups] == [2, 3]
    assert player.level == 3
    assert player.xp == 3
