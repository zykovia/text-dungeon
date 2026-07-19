from __future__ import annotations

from .models import Player


def record(player: Player, text: str) -> None:
    player.history.append(text)


def start_new_dungeon(player: Player) -> None:
    """Mark the current point in the log as the start of a new dungeon."""
    player.dungeon_history_start = len(player.history)


def current_dungeon_history(player: Player) -> list[str]:
    return player.history[player.dungeon_history_start :]
