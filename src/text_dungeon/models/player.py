from dataclasses import dataclass, field

from .item import Item


@dataclass
class Player:
    name: str
    player_class: str
    hp: int = 20
    max_hp: int = 20
    attack: int = 3
    inventory: list[Item] = field(default_factory=list)
    current_room: str = "entrance"
    visited: set[str] = field(default_factory=set)
    level: int = 1
    xp: int = 0
    dungeon_level: int = 1
    history: list[str] = field(default_factory=list)
    dungeon_history_start: int = 0

    @property
    def alive(self) -> bool:
        return self.hp > 0
