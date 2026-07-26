from text_dungeon.models import Item
from text_dungeon.shop import buy_price, sell_price
from text_dungeon.templates import ItemTemplate


def test_sell_price_for_tiered_gear():
    sword = Item("steel sword", "A sharp blade.", slot="main_hand", tier=3)
    shield = Item("iron shield", "A sturdy shield.", slot="off_hand", tier=2)

    assert sell_price(sword) == 6
    assert sell_price(shield) == 4


def test_buy_price_for_tiered_gear():
    template = ItemTemplate("steel sword", "A sharp blade.", slot="main_hand", tier=3)

    assert buy_price(template) == 12


def test_sell_and_buy_price_for_bandage():
    bandage = Item("bandage", "Rough cloth.", heal=4)
    template = ItemTemplate("bandage", "Rough cloth.", heal=4)

    assert sell_price(bandage) == 2
    assert buy_price(template) == 3


def test_sell_and_buy_price_for_health_potion():
    potion = Item("health potion", "Mends wounds.", heal=8)
    template = ItemTemplate("health potion", "Mends wounds.", heal=8)

    assert sell_price(potion) == 4
    assert buy_price(template) == 6


def test_sell_and_buy_price_for_mana_potion():
    potion = Item("mana potion", "Restores energy.", mana=6)
    template = ItemTemplate("mana potion", "Restores energy.", mana=6)

    assert sell_price(potion) == 4
    assert buy_price(template) == 6
