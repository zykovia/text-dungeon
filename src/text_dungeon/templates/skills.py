from dataclasses import dataclass


@dataclass(frozen=True)
class SkillTemplate:
    name: str
    description: str
    player_class: str
    unlock_level: int
    mana_cost: int
    heal: int = 0
    attack_buff: int = 0
    block: bool = False
    monster_attack_debuff: int = 0


SKILL_TEMPLATES = [
    SkillTemplate(
        "rally",
        "A battle cry that steadies your nerves and closes a wound.",
        player_class="Warrior",
        unlock_level=1,
        mana_cost=2,
        heal=4,
    ),
    SkillTemplate(
        "shield bash",
        "Slam your shield into your foe, throwing off their next strike.",
        player_class="Warrior",
        unlock_level=2,
        mana_cost=3,
        block=True,
    ),
    SkillTemplate(
        "cleave",
        "A wide, heavy swing that follows through with extra force.",
        player_class="Warrior",
        unlock_level=4,
        mana_cost=4,
        attack_buff=4,
    ),
    SkillTemplate(
        "second wind",
        "Dig deep and recover from wounds that would fell a lesser fighter.",
        player_class="Warrior",
        unlock_level=6,
        mana_cost=6,
        heal=10,
    ),
    SkillTemplate(
        "quick shot",
        "A snap shot loosed before your foe can react.",
        player_class="Ranger",
        unlock_level=1,
        mana_cost=2,
        attack_buff=2,
    ),
    SkillTemplate(
        "snare",
        "A hidden trap that hobbles your foe's next attack.",
        player_class="Ranger",
        unlock_level=2,
        mana_cost=3,
        monster_attack_debuff=3,
    ),
    SkillTemplate(
        "evasion",
        "Slip aside at the last instant, letting the blow find nothing.",
        player_class="Ranger",
        unlock_level=4,
        mana_cost=4,
        block=True,
    ),
    SkillTemplate(
        "precise strike",
        "A carefully aimed shot that finds the gap in any guard.",
        player_class="Ranger",
        unlock_level=6,
        mana_cost=6,
        attack_buff=6,
    ),
    SkillTemplate(
        "heal",
        "A soft prayer that knits flesh and bone back together.",
        player_class="Cleric",
        unlock_level=1,
        mana_cost=3,
        heal=6,
    ),
    SkillTemplate(
        "bless",
        "A blessing that steels your arm for the next strike.",
        player_class="Cleric",
        unlock_level=2,
        mana_cost=3,
        attack_buff=3,
    ),
    SkillTemplate(
        "divine shield",
        "A shimmering ward that turns aside the next blow entirely.",
        player_class="Cleric",
        unlock_level=4,
        mana_cost=4,
        block=True,
    ),
    SkillTemplate(
        "smite",
        "Call down holy judgment upon your foe.",
        player_class="Cleric",
        unlock_level=6,
        mana_cost=6,
        attack_buff=7,
    ),
    SkillTemplate(
        "frost bolt",
        "A shard of ice that stings your foe and slows their next attack.",
        player_class="Wizard",
        unlock_level=1,
        mana_cost=3,
        attack_buff=2,
        monster_attack_debuff=2,
    ),
    SkillTemplate(
        "arcane shield",
        "A shimmering barrier of raw magic that absorbs the next blow.",
        player_class="Wizard",
        unlock_level=2,
        mana_cost=3,
        block=True,
    ),
    SkillTemplate(
        "drain life",
        "Siphon your foe's vitality into your next strike.",
        player_class="Wizard",
        unlock_level=4,
        mana_cost=5,
        attack_buff=3,
        heal=3,
    ),
    SkillTemplate(
        "fireball",
        "An explosive burst of flame, the wizard's ultimate offense.",
        player_class="Wizard",
        unlock_level=6,
        mana_cost=8,
        attack_buff=8,
    ),
]
