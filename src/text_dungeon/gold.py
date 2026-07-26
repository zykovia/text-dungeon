from .balance import BOSS_GOLD, MONSTER_GOLD


def gold_for_kill(monster_name: str, boss_name: str, super_boss_name: str | None = None) -> int:
    """Gold awarded for killing a monster: a flat bonus for a boss (regular or final)."""
    if monster_name in (boss_name, super_boss_name):
        return BOSS_GOLD
    return MONSTER_GOLD
