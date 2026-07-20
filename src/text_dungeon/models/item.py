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

    def effect_summary(self) -> str:
        """Player-facing summary of this item's mechanical effect, if any."""
        parts = []
        if self.damage_bonus:
            parts.append(f"+{self.damage_bonus} damage")
        if self.defense_bonus:
            parts.append(f"+{self.defense_bonus} armor")
        if self.heal:
            parts.append(f"heals {self.heal} HP")
        return ", ".join(parts)
