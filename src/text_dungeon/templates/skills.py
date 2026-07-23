from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Sequence

if TYPE_CHECKING:
    from ..models import Player


class SkillEffect(ABC):
    """One mechanical outcome of casting a skill.

    New effect types (poison, stun, lifesteal, ...) are added by writing a
    new subclass here, not by extending branching logic elsewhere.
    """

    @abstractmethod
    def describe(self) -> str:
        """Player-facing summary of the mechanical outcome."""

    @abstractmethod
    def apply(self, player: Player, skill_name: str, allies: Sequence[Player] = ()) -> str:
        """Mutate `player` (and possibly `allies`) in place, return a message to emit."""


@dataclass(frozen=True)
class Heal(SkillEffect):
    amount: int

    def describe(self) -> str:
        return f"heals {self.amount} HP"

    def apply(self, player: Player, skill_name: str, allies: Sequence[Player] = ()) -> str:
        healed = min(self.amount, player.max_hp - player.hp)
        player.hp += healed
        return f"You cast {skill_name} and recover {healed} HP. ({player.hp}/{player.max_hp} HP)"


@dataclass(frozen=True)
class HealAllies(SkillEffect):
    """Like Heal, but also mends any ally passed in - used only by the
    Cleric's "heal" skill, not the other classes' self-only heals."""

    amount: int

    def describe(self) -> str:
        return f"heals {self.amount} HP (also nearby allies)"

    def apply(self, player: Player, skill_name: str, allies: Sequence[Player] = ()) -> str:
        healed = min(self.amount, player.max_hp - player.hp)
        player.hp += healed
        for ally in allies:
            ally.hp = min(ally.max_hp, ally.hp + self.amount)
        message = f"You cast {skill_name} and recover {healed} HP. ({player.hp}/{player.max_hp} HP)"
        if allies:
            message += f" Your prayer washes over {len(allies)} nearby ally(ies)."
        return message


@dataclass(frozen=True)
class AttackBuff(SkillEffect):
    amount: int

    def describe(self) -> str:
        return f"+{self.amount} to your next attack"

    def apply(self, player: Player, skill_name: str, allies: Sequence[Player] = ()) -> str:
        player.pending_attack_buff += self.amount
        return f"You channel {skill_name}, empowering your next attack."


@dataclass(frozen=True)
class Block(SkillEffect):
    def describe(self) -> str:
        return "blocks the monster's next attack"

    def apply(self, player: Player, skill_name: str, allies: Sequence[Player] = ()) -> str:
        player.pending_block = True
        return f"You cast {skill_name}, readying yourself to block the next blow."


@dataclass(frozen=True)
class MonsterDebuff(SkillEffect):
    amount: int

    def describe(self) -> str:
        return f"-{self.amount} to the monster's next attack"

    def apply(self, player: Player, skill_name: str, allies: Sequence[Player] = ()) -> str:
        player.pending_monster_debuff += self.amount
        return f"You cast {skill_name}, weakening your foe's next strike."


@dataclass(frozen=True)
class SkillTemplate:
    name: str
    description: str
    player_class: str
    unlock_level: int
    mana_cost: int
    effects: tuple[SkillEffect, ...] = ()

    def effect_summary(self) -> str:
        return "; ".join(effect.describe() for effect in self.effects)


SKILL_TEMPLATES = [
    SkillTemplate(
        "rally",
        "A battle cry that steadies your nerves and closes a wound.",
        player_class="Warrior",
        unlock_level=1,
        mana_cost=2,
        effects=(Heal(4),),
    ),
    SkillTemplate(
        "shield bash",
        "Slam your shield into your foe, throwing off their next strike.",
        player_class="Warrior",
        unlock_level=2,
        mana_cost=3,
        effects=(Block(),),
    ),
    SkillTemplate(
        "cleave",
        "A wide, heavy swing that follows through with extra force.",
        player_class="Warrior",
        unlock_level=4,
        mana_cost=4,
        effects=(AttackBuff(4),),
    ),
    SkillTemplate(
        "second wind",
        "Dig deep and recover from wounds that would fell a lesser fighter.",
        player_class="Warrior",
        unlock_level=6,
        mana_cost=6,
        effects=(Heal(10),),
    ),
    SkillTemplate(
        "quick shot",
        "A snap shot loosed before your foe can react.",
        player_class="Ranger",
        unlock_level=1,
        mana_cost=2,
        effects=(AttackBuff(2),),
    ),
    SkillTemplate(
        "snare",
        "A hidden trap that hobbles your foe's next attack.",
        player_class="Ranger",
        unlock_level=2,
        mana_cost=3,
        effects=(MonsterDebuff(3),),
    ),
    SkillTemplate(
        "evasion",
        "Slip aside at the last instant, letting the blow find nothing.",
        player_class="Ranger",
        unlock_level=4,
        mana_cost=4,
        effects=(Block(),),
    ),
    SkillTemplate(
        "precise strike",
        "A carefully aimed shot that finds the gap in any guard.",
        player_class="Ranger",
        unlock_level=6,
        mana_cost=6,
        effects=(AttackBuff(6),),
    ),
    SkillTemplate(
        "heal",
        "A soft prayer that knits flesh and bone back together.",
        player_class="Cleric",
        unlock_level=1,
        mana_cost=3,
        effects=(HealAllies(6),),
    ),
    SkillTemplate(
        "bless",
        "A blessing that steels your arm for the next strike.",
        player_class="Cleric",
        unlock_level=2,
        mana_cost=3,
        effects=(AttackBuff(3),),
    ),
    SkillTemplate(
        "divine shield",
        "A shimmering ward that turns aside the next blow entirely.",
        player_class="Cleric",
        unlock_level=4,
        mana_cost=4,
        effects=(Block(),),
    ),
    SkillTemplate(
        "smite",
        "Call down holy judgment upon your foe.",
        player_class="Cleric",
        unlock_level=6,
        mana_cost=6,
        effects=(AttackBuff(7),),
    ),
    SkillTemplate(
        "frost bolt",
        "A shard of ice that stings your foe and slows their next attack.",
        player_class="Wizard",
        unlock_level=1,
        mana_cost=3,
        effects=(AttackBuff(2), MonsterDebuff(2)),
    ),
    SkillTemplate(
        "arcane shield",
        "A shimmering barrier of raw magic that absorbs the next blow.",
        player_class="Wizard",
        unlock_level=2,
        mana_cost=3,
        effects=(Block(),),
    ),
    SkillTemplate(
        "drain life",
        "Siphon your foe's vitality into your next strike.",
        player_class="Wizard",
        unlock_level=4,
        mana_cost=5,
        effects=(AttackBuff(3), Heal(3)),
    ),
    SkillTemplate(
        "fireball",
        "An explosive burst of flame, the wizard's ultimate offense.",
        player_class="Wizard",
        unlock_level=6,
        mana_cost=8,
        effects=(AttackBuff(8),),
    ),
]


def skill_template_for(skill_name: str) -> SkillTemplate | None:
    """The template for a known skill by name, if any."""
    return next((skill for skill in SKILL_TEMPLATES if skill.name == skill_name), None)
