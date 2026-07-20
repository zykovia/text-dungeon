from __future__ import annotations

from dataclasses import dataclass

from .balance import BOSS_XP, LEVEL_UP_HP_BONUS, MONSTER_XP, SUPER_BOSS_XP, XP_PER_LEVEL
from .models import Player
from .templates import SKILL_TEMPLATES


@dataclass
class LevelUp:
    level: int
    max_hp: int
    skill_learned: str | None = None


def xp_for_kill(monster_name: str, boss_name: str, super_boss_name: str | None = None) -> int:
    if monster_name == super_boss_name:
        return SUPER_BOSS_XP
    if monster_name == boss_name:
        return BOSS_XP
    return MONSTER_XP


def _skill_unlocked_at(player_class: str, level: int) -> str | None:
    return next(
        (
            skill.name
            for skill in SKILL_TEMPLATES
            if skill.player_class == player_class and skill.unlock_level == level
        ),
        None,
    )


def gain_xp(player: Player, amount: int) -> list[LevelUp]:
    """Apply an XP gain to `player`, in place, returning any level-ups triggered, in order."""
    player.xp += amount
    level_ups = []
    while player.xp >= XP_PER_LEVEL:
        player.xp -= XP_PER_LEVEL
        player.level += 1
        player.max_hp += LEVEL_UP_HP_BONUS
        player.hp = player.max_hp
        player.mana = player.max_mana
        skill_learned = _skill_unlocked_at(player.player_class, player.level)
        if skill_learned is not None:
            player.skills.append(skill_learned)
        level_ups.append(
            LevelUp(level=player.level, max_hp=player.max_hp, skill_learned=skill_learned)
        )
    return level_ups
