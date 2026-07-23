from text_dungeon.models import Player
from text_dungeon.skills import apply_skill
from text_dungeon.templates.skills import (
    SKILL_TEMPLATES,
    AttackBuff,
    Block,
    Heal,
    HealAllies,
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


def test_heal_allies_effect_heals_self_with_no_allies_like_plain_heal():
    effect = HealAllies(6)
    player = Player(name="test", player_class="Cleric", hp=10, max_hp=20)

    assert effect.describe() == "heals 6 HP (also nearby allies)"
    message = effect.apply(player, "heal")

    assert player.hp == 16
    assert "recover 6 HP" in message
    assert "ally" not in message


def test_heal_allies_effect_heals_every_ally_in_range():
    effect = HealAllies(6)
    player = Player(name="caster", player_class="Cleric", hp=10, max_hp=20)
    ally_a = Player(name="a", player_class="Warrior", hp=5, max_hp=20)
    ally_b = Player(name="b", player_class="Ranger", hp=8, max_hp=20)

    message = effect.apply(player, "heal", [ally_a, ally_b])

    assert player.hp == 16
    assert ally_a.hp == 11
    assert ally_b.hp == 14
    assert "2 nearby ally(ies)" in message


def test_heal_allies_effect_caps_each_ally_individually_at_their_own_max_hp():
    effect = HealAllies(10)
    player = Player(name="caster", player_class="Cleric", hp=20, max_hp=20)
    nearly_full = Player(name="a", player_class="Warrior", hp=18, max_hp=20)

    effect.apply(player, "heal", [nearly_full])

    assert nearly_full.hp == 20


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


def test_apply_skill_deducts_mana_and_marks_used_this_round():
    player = Player(name="test", player_class="Warrior", mana=5, max_mana=5, hp=10, max_hp=20)
    skill = _skill("rally")

    messages = apply_skill(player, skill)

    assert player.mana == 3
    assert player.used_skills_this_round == {"rally"}
    assert player.hp == 14
    assert messages == ["You cast rally and recover 4 HP. (14/20 HP)"]


def test_apply_skill_returns_one_message_per_effect():
    player = Player(name="test", player_class="Wizard", mana=10, max_mana=10)
    skill = _skill("drain life")

    messages = apply_skill(player, skill)

    assert len(messages) == len(skill.effects) == 2
