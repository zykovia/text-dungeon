from __future__ import annotations

from .models import Item, Player
from .templates import CLASS_TEMPLATES, ITEM_TEMPLATES, ClassTemplate

DEFAULT_PLAYER_CLASS = CLASS_TEMPLATES[0].name
CLASS_NAMES = [template.name for template in CLASS_TEMPLATES]


def _class_template(player_class: str) -> ClassTemplate:
    for template in CLASS_TEMPLATES:
        if template.name == player_class:
            return template
    raise ValueError(f"Unknown class: {player_class!r}")


def _starting_item(class_template: ClassTemplate) -> Item:
    item_template = next(t for t in ITEM_TEMPLATES if t.name == class_template.starting_item)
    return Item(
        item_template.name,
        item_template.description,
        heal=item_template.heal,
        damage_bonus=item_template.damage_bonus,
        player_class=item_template.player_class,
    )


def create_player(player_class: str, name: str = "Adventurer") -> Player:
    """Build a fresh Player with the given class's starting stats and gear."""
    template = _class_template(player_class)
    return Player(
        name=name,
        player_class=template.name,
        hp=template.starting_hp,
        max_hp=template.starting_hp,
        attack=template.starting_attack,
        inventory=[_starting_item(template)],
    )
