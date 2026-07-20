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
    """Apply one round of the player attacking `monster`, mutating both in place.

    Any skill cast beforehand (`Player.pending_*`) applies to this round only,
    then is cleared regardless of outcome.
    """
    equipped = [item for item in (player.main_hand, player.off_hand) if item]
    bonus = sum(item.damage_bonus for item in equipped) + player.pending_attack_buff
    defense = sum(item.defense_bonus for item in equipped)
    monster_attack = max(0, monster.attack - player.pending_monster_debuff)
    block = player.pending_block

    player.pending_attack_buff = 0
    player.pending_block = False
    player.pending_monster_debuff = 0

    damage = player.attack + bonus + random.randint(*ATTACK_DAMAGE_ROLL)
    monster.hp -= damage

    if not monster.alive:
        return AttackResult(damage_dealt=damage, monster_defeated=True)

    incoming = 0 if block else max(0, monster_attack + random.randint(*INCOMING_DAMAGE_ROLL) - defense)
    player.hp -= incoming
    return AttackResult(damage_dealt=damage, monster_defeated=False, incoming_damage=incoming)
