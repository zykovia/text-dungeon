from text_dungeon.models import Player
from text_dungeon.templates.skills import (
    SKILL_TEMPLATES,
    AttackBuff,
    Block,
    Heal,
    MonsterDebuff,
    SkillTemplate,
)


def _skill(name: str) -> SkillTemplate:
    return next(s for s in SKILL_TEMPLATES if s.name == name)


def test_heal_effect_describes_and_applies():
    effect = Heal(4)
    player = Player(name="test", player_class="Warrior", hp=10, max_hp=20)

    assert effect.describe() == "heals 4 HP"
    message = effect.apply(player, "rally")

    assert player.hp == 14
    assert "recover 4 HP" in message


def test_heal_effect_caps_at_max_hp():
    effect = Heal(10)
    player = Player(name="test", player_class="Warrior", hp=18, max_hp=20)

    effect.apply(player, "rally")

    assert player.hp == 20


def test_attack_buff_effect_describes_and_applies():
    effect = AttackBuff(4)
    player = Player(name="test", player_class="Warrior")

    assert effect.describe() == "+4 to your next attack"
    effect.apply(player, "cleave")

    assert player.pending_attack_buff == 4


def test_block_effect_describes_and_applies():
    effect = Block()
    player = Player(name="test", player_class="Warrior")

    assert effect.describe() == "blocks the monster's next attack"
    effect.apply(player, "shield bash")

    assert player.pending_block is True


def test_monster_debuff_effect_describes_and_applies():
    effect = MonsterDebuff(3)
    player = Player(name="test", player_class="Ranger")

    assert effect.describe() == "-3 to the monster's next attack"
    effect.apply(player, "snare")

    assert player.pending_monster_debuff == 3


def test_skill_effect_summary_joins_multiple_effects():
    skill = _skill("drain life")

    assert skill.effect_summary() == "+3 to your next attack; heals 3 HP"


def test_skill_effect_summary_for_single_effect_skill():
    skill = _skill("shield bash")

    assert skill.effect_summary() == "blocks the monster's next attack"
