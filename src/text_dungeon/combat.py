from __future__ import annotations

import random
from dataclasses import dataclass

from .balance import ATTACK_DAMAGE_ROLL, INCOMING_DAMAGE_ROLL
from .models import Monster, Player


@dataclass
class AttackResult:
    damage_dealt: int
    monster_defeated: bool
    incoming_damage: int = 0


def resolve_attack(player: Player, monster: Monster) -> AttackResult:
    """Apply one round of the player attacking `monster`, mutating both in place."""
    equipped = [item for item in (player.main_hand, player.off_hand) if item]
    bonus = sum(item.damage_bonus for item in equipped)
    defense = sum(item.defense_bonus for item in equipped)

    damage = player.attack + bonus + random.randint(*ATTACK_DAMAGE_ROLL)
    monster.hp -= damage

    if not monster.alive:
        return AttackResult(damage_dealt=damage, monster_defeated=True)

    incoming = max(0, monster.attack + random.randint(*INCOMING_DAMAGE_ROLL) - defense)
    player.hp -= incoming
    return AttackResult(damage_dealt=damage, monster_defeated=False, incoming_damage=incoming)
