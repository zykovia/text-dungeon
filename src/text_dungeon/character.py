from __future__ import annotations

from .items import item_from_template
from .models import Item, Player
from .templates import CLASS_TEMPLATES, ITEM_TEMPLATES, ClassTemplate, ItemTemplate

DEFAULT_PLAYER_CLASS = CLASS_TEMPLATES[0].name
CLASS_NAMES = [template.name for template in CLASS_TEMPLATES]


def _class_template(player_class: str) -> ClassTemplate:
    for template in CLASS_TEMPLATES:
        if template.name == player_class:
            return template
    raise ValueError(f"Unknown class: {player_class!r}")


def _item_template(item_name: str) -> ItemTemplate:
    return next(t for t in ITEM_TEMPLATES if t.name == item_name)


def _starting_item(item_name: str) -> Item:
    return item_from_template(_item_template(item_name))


def default_name_for_class(player_class: str) -> str:
    """The suggested adventurer name for a class, offered when the player picks no other."""
    return _class_template(player_class).default_name


def create_player(player_class: str, name: str | None = None) -> Player:
    """Build a fresh Player with the given class's starting stats and gear.

    A name left unset falls back to the class's default name.
    """
    template = _class_template(player_class)
    return Player(
        name=name or template.default_name,
        player_class=template.name,
        hp=template.starting_hp,
        max_hp=template.starting_hp,
        attack=template.starting_attack,
        main_hand=_starting_item(template.starting_item),
        off_hand=_starting_item(template.starting_offhand_item),
    )
