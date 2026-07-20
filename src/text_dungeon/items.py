from .models import Item
from .templates import ItemTemplate


def item_from_template(template: ItemTemplate) -> Item:
    """The single place an Item is built from a template, so every field carries over."""
    return Item(
        template.name,
        template.description,
        heal=template.heal,
        damage_bonus=template.damage_bonus,
        player_class=template.player_class,
        slot=template.slot,
        defense_bonus=template.defense_bonus,
        tier=template.tier,
    )
