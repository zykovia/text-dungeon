from dataclasses import dataclass


@dataclass(frozen=True)
class ItemTemplate:
    name: str
    description: str
    heal: int = 0
    damage_bonus: int = 0
    player_class: str | None = None


ITEM_TEMPLATES = [
    ItemTemplate(
        "rusty sword", "A worn blade, better than fists.", damage_bonus=2, player_class="Warrior"
    ),
    ItemTemplate("health potion", "A vial of red liquid that mends wounds.", heal=8),
    ItemTemplate(
        "dagger", "Quick and sharp, easy to conceal.", damage_bonus=1, player_class="Ranger"
    ),
    ItemTemplate("bandage", "Rough cloth, better than nothing.", heal=4),
    ItemTemplate(
        "mace",
        "A heavy, blunt weapon blessed for battle.",
        damage_bonus=2,
        player_class="Cleric",
    ),
    ItemTemplate(
        "apprentice staff",
        "A gnarled length of wood humming with latent power.",
        damage_bonus=3,
        player_class="Wizard",
    ),
]
