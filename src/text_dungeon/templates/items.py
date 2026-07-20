from dataclasses import dataclass


@dataclass(frozen=True)
class ItemTemplate:
    name: str
    description: str
    heal: int = 0
    damage_bonus: int = 0
    player_class: str | None = None
    slot: str | None = None
    defense_bonus: int = 0


ITEM_TEMPLATES = [
    ItemTemplate(
        "rusty sword",
        "A worn blade, better than fists.",
        damage_bonus=2,
        player_class="Warrior",
        slot="main_hand",
    ),
    ItemTemplate("health potion", "A vial of red liquid that mends wounds.", heal=8),
    ItemTemplate(
        "dagger",
        "Quick and sharp, easy to conceal.",
        damage_bonus=1,
        player_class="Ranger",
        slot="main_hand",
    ),
    ItemTemplate("bandage", "Rough cloth, better than nothing.", heal=4),
    ItemTemplate(
        "mace",
        "A heavy, blunt weapon blessed for battle.",
        damage_bonus=2,
        player_class="Cleric",
        slot="main_hand",
    ),
    ItemTemplate(
        "apprentice staff",
        "A gnarled length of wood humming with latent power.",
        damage_bonus=3,
        player_class="Wizard",
        slot="main_hand",
    ),
    ItemTemplate(
        "wooden shield",
        "A sturdy round shield, scarred from old blows.",
        defense_bonus=2,
        player_class="Warrior",
        slot="off_hand",
    ),
    ItemTemplate(
        "hunting knife",
        "A second blade for a second strike.",
        damage_bonus=1,
        player_class="Ranger",
        slot="off_hand",
    ),
    ItemTemplate(
        "holy symbol",
        "A blessed emblem that turns aside harm.",
        defense_bonus=1,
        player_class="Cleric",
        slot="off_hand",
    ),
    ItemTemplate(
        "spellbook",
        "A well-worn tome of minor incantations.",
        damage_bonus=1,
        player_class="Wizard",
        slot="off_hand",
    ),
]
