from dataclasses import dataclass


@dataclass
class Monster:
    name: str
    hp: int
    attack: int
    description: str = ""
    xp: int = 0
    gold: int = 0

    @property
    def alive(self) -> bool:
        return self.hp > 0
