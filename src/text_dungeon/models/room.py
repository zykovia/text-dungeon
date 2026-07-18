from dataclasses import dataclass, field

from .item import Item
from .monster import Monster


@dataclass
class Room:
    id: str
    name: str
    description: str
    exits: dict[str, str] = field(default_factory=dict)
    items: list[Item] = field(default_factory=list)
    monster: Monster | None = None
