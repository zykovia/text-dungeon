from dataclasses import dataclass


@dataclass
class Monster:
    name: str
    hp: int
    attack: int
    description: str = ""

    @property
    def alive(self) -> bool:
        return self.hp > 0
