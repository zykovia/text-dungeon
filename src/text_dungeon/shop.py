from .balance import (
    BANDAGE_BUY_GOLD,
    BANDAGE_SELL_GOLD,
    HEALTH_POTION_BUY_GOLD,
    HEALTH_POTION_SELL_GOLD,
    MANA_POTION_BUY_GOLD,
    MANA_POTION_SELL_GOLD,
    WEAPON_BUY_GOLD_PER_TIER,
    WEAPON_SELL_GOLD_PER_TIER,
)
from .models import Item
from .templates import ItemTemplate

_POTION_SELL_PRICES = {
    "bandage": BANDAGE_SELL_GOLD,
    "health potion": HEALTH_POTION_SELL_GOLD,
    "mana potion": MANA_POTION_SELL_GOLD,
}

_POTION_BUY_PRICES = {
    "bandage": BANDAGE_BUY_GOLD,
    "health potion": HEALTH_POTION_BUY_GOLD,
    "mana potion": MANA_POTION_BUY_GOLD,
}


def sell_price(item: Item) -> int:
    """Gold refunded for selling an item: per-tier for equippable gear, flat for potions."""
    if item.slot is not None:
        return item.tier * WEAPON_SELL_GOLD_PER_TIER
    return _POTION_SELL_PRICES.get(item.name, 0)


def buy_price(template: ItemTemplate) -> int:
    """Gold cost to buy an item from the shop: per-tier for equippable gear, flat for potions."""
    if template.slot is not None:
        return template.tier * WEAPON_BUY_GOLD_PER_TIER
    return _POTION_BUY_PRICES.get(template.name, 0)
