from __future__ import annotations

from typing import Sequence

from .models import Player
from .templates import SkillTemplate


def apply_skill(player: Player, skill: SkillTemplate, allies: Sequence[Player] = ()) -> list[str]:
    """Pay the mana cost, mark the skill used this round, and apply its effects in place.

    `allies` is only used by effects that affect more than the caster (e.g.
    HealAllies); other effects ignore it.

    Returns the player-facing message for each effect applied, in order.
    """
    player.mana -= skill.mana_cost
    player.used_skills_this_round.add(skill.name)
    return [effect.apply(player, skill.name, allies) for effect in skill.effects]
