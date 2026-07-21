from __future__ import annotations

from dataclasses import dataclass

from .models import Item, Player, Room


@dataclass
class TakeResult:
    item: Item | None
    blocked_by_class: bool = False


def take_item(player: Player, room: Room, item_name: str) -> TakeResult:
    """Move `item_name` from `room` into `player`'s inventory, if present and takeable."""
    for item in room.items:
        if item.name == item_name:
            if item.player_class is not None and item.player_class != player.player_class:
                return TakeResult(item=item, blocked_by_class=True)
            room.items.remove(item)
            player.inventory.append(item)
            return TakeResult(item=item)
    return TakeResult(item=None)


def equip_item(player: Player, item: Item) -> Item | None:
    """Equip `item` (already confirmed to be in inventory and equippable) into its slot.

    Returns whichever item previously occupied that slot, after marking it
    retired and returning it to inventory, or None if the slot was empty.
    """
    previous = getattr(player, item.slot)
    if previous is not None:
        previous.retired = True
        player.inventory.append(previous)
    item.retired = False
    player.inventory.remove(item)
    setattr(player, item.slot, item)
    return previous


def unequip_item(player: Player, item_name: str) -> Item | None:
    """Move the item named `item_name` out of whichever slot holds it, back to inventory."""
    for slot in ("main_hand", "off_hand"):
        item = getattr(player, slot)
        if item is not None and item.name == item_name:
            setattr(player, slot, None)
            player.inventory.append(item)
            return item
    return None


@dataclass
class UseResult:
    item: Item | None
    healed: int = 0


def use_item(player: Player, item_name: str) -> UseResult:
    """Consume the item named `item_name` from inventory, if present and usable (heals)."""
    for item in player.inventory:
        if item.name == item_name:
            if not item.heal:
                return UseResult(item=item, healed=0)
            healed = min(item.heal, player.max_hp - player.hp)
            player.hp += healed
            player.inventory.remove(item)
            return UseResult(item=item, healed=healed)
    return UseResult(item=None)


def item_label(item: Item) -> str:
    """An item's name plus its mechanical effect, e.g. 'rusty sword (+2 damage)'."""
    effect = item.effect_summary()
    return f"{item.name} ({effect})" if effect else item.name


def equipped_line(item: Item | None) -> str:
    return f"{item_label(item)}: {item.description}" if item else "(empty)"


def item_summary(item: Item | None) -> dict | None:
    if not item:
        return None
    return {
        "name": item.name,
        "description": item.description,
        "effect": item.effect_summary(),
    }


def inventory_lines(player: Player) -> list[str]:
    """Player-facing lines for the `inventory` command: equipment, then carried items.

    Items bumped out of a slot by a later upgrade are flagged retired and
    collapse into a single "Old gear (N)" line instead of one entry each.
    """
    lines = [
        f"Main hand: {equipped_line(player.main_hand)}",
        f"Off hand: {equipped_line(player.off_hand)}",
    ]
    active = [item for item in player.inventory if not item.retired]
    retired = [item for item in player.inventory if item.retired]
    if not active and not retired:
        lines.append("You aren't carrying anything else.")
        return lines
    for item in active:
        lines.append(f"- {item_label(item)}: {item.description}")
    if retired:
        names = ", ".join(item.name for item in retired)
        lines.append(f"- Old gear ({len(retired)}): {names}")
    return lines
