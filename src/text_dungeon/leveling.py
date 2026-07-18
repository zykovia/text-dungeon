from __future__ import annotations

from dataclasses import dataclass

from .models import Player

MONSTER_XP = 2
BOSS_XP = 5
XP_PER_LEVEL = 10
LEVEL_UP_HP_BONUS = 5


@dataclass
class LevelUp:
    level: int
    max_hp: int


def xp_for_kill(monster_name: str, boss_name: str) -> int:
    return BOSS_XP if monster_name == boss_name else MONSTER_XP


def gain_xp(player: Player, amount: int) -> list[LevelUp]:
    """Apply an XP gain to `player`, in place, returning any level-ups triggered, in order."""
    player.xp += amount
    level_ups = []
    while player.xp >= XP_PER_LEVEL:
        player.xp -= XP_PER_LEVEL
        player.level += 1
        player.max_hp += LEVEL_UP_HP_BONUS
        player.hp = player.max_hp
        level_ups.append(LevelUp(level=player.level, max_hp=player.max_hp))
    return level_ups
