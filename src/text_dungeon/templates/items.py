from dataclasses import dataclass


@dataclass(frozen=True)
class ItemTemplate:
    name: str
    description: str
    heal: int = 0
    damage_bonus: int = 0


ITEM_TEMPLATES = [
    ItemTemplate("rusty sword", "A worn blade, better than fists.", damage_bonus=2),
    ItemTemplate("health potion", "A vial of red liquid that mends wounds.", heal=8),
    ItemTemplate("dagger", "Quick and sharp, easy to conceal.", damage_bonus=1),
    ItemTemplate("bandage", "Rough cloth, better than nothing.", heal=4),
]
