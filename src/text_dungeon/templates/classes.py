from dataclasses import dataclass


@dataclass(frozen=True)
class ClassTemplate:
    name: str
    description: str
    starting_hp: int
    starting_attack: int
    starting_item: str
    starting_offhand_item: str
    default_name: str


CLASS_TEMPLATES = [
    ClassTemplate(
        "Warrior",
        "A hardened fighter who wades into melee and shrugs off punishment.",
        starting_hp=24,
        starting_attack=4,
        starting_item="rusty sword",
        starting_offhand_item="wooden shield",
        default_name="Mulan",
    ),
    ClassTemplate(
        "Ranger",
        "A quick, self-sufficient scout, equally at home stalking prey or foes.",
        starting_hp=20,
        starting_attack=3,
        starting_item="dagger",
        starting_offhand_item="hunting knife",
        default_name="Hippolyta",
    ),
    ClassTemplate(
        "Cleric",
        "A devoted warrior-priest whose faith is as sturdy as their mace.",
        starting_hp=22,
        starting_attack=3,
        starting_item="mace",
        starting_offhand_item="holy symbol",
        default_name="Margaret",
    ),
    ClassTemplate(
        "Wizard",
        "A frail but dangerous spellcaster, trading toughness for raw power.",
        starting_hp=16,
        starting_attack=2,
        starting_item="apprentice staff",
        starting_offhand_item="spellbook",
        default_name="Yennefer",
    ),
]
