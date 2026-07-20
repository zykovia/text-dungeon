from dataclasses import dataclass


@dataclass
class Item:
    name: str
    description: str
    heal: int = 0
    damage_bonus: int = 0
    player_class: str | None = None
    slot: str | None = None
    defense_bonus: int = 0
    tier: int = 1
