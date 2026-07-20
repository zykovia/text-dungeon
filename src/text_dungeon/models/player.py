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
    main_hand: Item | None = None
    off_hand: Item | None = None
    mana: int = 0
    max_mana: int = 0
    skills: list[str] = field(default_factory=list)
    pending_attack_buff: int = 0
    pending_block: bool = False
    pending_monster_debuff: int = 0
    used_skills_this_round: set[str] = field(default_factory=set)
    current_room: str = "entrance"
    visited: set[str] = field(default_factory=set)
    level: int = 1
    xp: int = 0
    dungeon_level: int = 1
    history: list[str] = field(default_factory=list)
    dungeon_history_start: int = 0
    next_upgrade_slot: str = "main_hand"

    @property
    def alive(self) -> bool:
        return self.hp > 0
