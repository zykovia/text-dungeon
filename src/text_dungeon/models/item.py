from dataclasses import dataclass


@dataclass
class Item:
    name: str
    description: str
    heal: int = 0
    damage_bonus: int = 0
