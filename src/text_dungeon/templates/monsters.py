from dataclasses import dataclass


@dataclass(frozen=True)
class MonsterTemplate:
    name: str
    min_hp: int
    max_hp: int
    attack: int
    description: str


MONSTER_TEMPLATES = [
    MonsterTemplate("skeleton", 8, 12, 2, "A rattling pile of animated bones."),
    MonsterTemplate("giant rat", 5, 8, 1, "Its eyes gleam red in the dark."),
    MonsterTemplate("cave spider", 6, 9, 2, "Venom drips from its mandibles."),
    MonsterTemplate("shade", 9, 13, 3, "A flicker of darkness given cruel shape."),
]
