from dataclasses import dataclass, field


@dataclass
class Item:
    name: str
    description: str
    heal: int = 0
    damage_bonus: int = 0


@dataclass
class Monster:
    name: str
    hp: int
    attack: int
    description: str = ""

    @property
    def alive(self) -> bool:
        return self.hp > 0


@dataclass
class Room:
    id: str
    name: str
    description: str
    exits: dict[str, str] = field(default_factory=dict)
    items: list[Item] = field(default_factory=list)
    monster: Monster | None = None


@dataclass
class Player:
    name: str
    hp: int = 20
    max_hp: int = 20
    attack: int = 3
    inventory: list[Item] = field(default_factory=list)
    current_room: str = "entrance"
    visited: set[str] = field(default_factory=set)
    level: int = 1
    xp: int = 0

    @property
    def alive(self) -> bool:
        return self.hp > 0
