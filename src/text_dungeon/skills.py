from __future__ import annotations

from .models import Player
from .templates import SkillTemplate


def apply_skill(player: Player, skill: SkillTemplate) -> list[str]:
    """Pay the mana cost, mark the skill used this round, and apply its effects in place.

    Returns the player-facing message for each effect applied, in order.
    """
    player.mana -= skill.mana_cost
    player.used_skills_this_round.add(skill.name)
    return [effect.apply(player, skill.name) for effect in skill.effects]
