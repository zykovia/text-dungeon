from __future__ import annotations

import dataclasses
import json
import os
from pathlib import Path

from .balance import MAX_DUNGEON_LEVEL
from .models import Item, Monster, Player, Room
from .world_state import World

# Bump this whenever a save produced by an older version of the game could crash
# or misbehave on load (e.g. a Player/Room field is added, renamed, or removed,
# or dungeon generation changes in a way old saves shouldn't carry forward).
# Saves tagged with a different version are discarded instead of being loaded.
SAVE_VERSION = 8


def default_save_dir() -> Path:
    configured = os.environ.get("TEXT_DUNGEON_SAVE_DIR")
    return Path(configured) if configured else Path.home() / ".text_dungeon" / "saves"


def _world_path(world_id: str, save_dir: Path | None) -> Path:
    return (save_dir or default_save_dir()) / world_id / "world.json"


def _player_path(world_id: str, player_id: str, save_dir: Path | None) -> Path:
    return (save_dir or default_save_dir()) / world_id / "players" / f"{player_id}.json"


def _read_state(path: Path) -> dict | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except (OSError, ValueError):
        return None


def _rooms_from_state(rooms_data: dict) -> dict[str, Room]:
    rooms = {}
    for room_id, room_data in rooms_data.items():
        room_data = dict(room_data)
        room_data["items"] = [Item(**item) for item in room_data["items"]]
        room_data["monster"] = (
            Monster(**room_data["monster"]) if room_data["monster"] is not None else None
        )
        rooms[room_id] = Room(**room_data)
    return rooms


def save_world(world_id: str, world: World, save_dir: Path | None = None) -> None:
    path = _world_path(world_id, save_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    state = {
        "version": SAVE_VERSION,
        "levels": {
            str(level): {room_id: dataclasses.asdict(room) for room_id, room in rooms.items()}
            for level, rooms in world.levels.items()
        },
    }
    path.write_text(json.dumps(state))


def load_world(world_id: str, save_dir: Path | None = None) -> World | None:
    path = _world_path(world_id, save_dir)
    state = _read_state(path)
    if state is None or state.get("version") != SAVE_VERSION:
        path.unlink(missing_ok=True)
        return None
    levels = {
        int(level_str): _rooms_from_state(rooms_data)
        for level_str, rooms_data in state["levels"].items()
    }
    return World(levels=levels)


def save_player(
    world_id: str, player_id: str, player: Player, running: bool, save_dir: Path | None = None
) -> None:
    path = _player_path(world_id, player_id, save_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    state = {
        "version": SAVE_VERSION,
        "player": dataclasses.asdict(player)
        | {
            "visited": sorted(player.visited),
            "used_skills_this_round": sorted(player.used_skills_this_round),
        },
        "running": running,
    }
    path.write_text(json.dumps(state))


def load_player(
    world_id: str, player_id: str, save_dir: Path | None = None
) -> tuple[Player, bool] | None:
    path = _player_path(world_id, player_id, save_dir)
    state = _read_state(path)
    if state is None or state.get("version") != SAVE_VERSION:
        path.unlink(missing_ok=True)
        return None
    player_data = dict(state["player"])
    player_data["inventory"] = [Item(**item) for item in player_data["inventory"]]
    player_data["main_hand"] = (
        Item(**player_data["main_hand"]) if player_data["main_hand"] is not None else None
    )
    player_data["off_hand"] = (
        Item(**player_data["off_hand"]) if player_data["off_hand"] is not None else None
    )
    player_data["visited"] = set(player_data["visited"])
    player_data["used_skills_this_round"] = set(player_data["used_skills_this_round"])
    return Player(**player_data), state["running"]


def load_summary(world_id: str, player_id: str, save_dir: Path | None = None) -> dict | None:
    """A lightweight, read-only peek at a save for the world-select screen.

    Never deletes an incompatible save (unlike load_player): this runs for every
    world just to render the select list, before the player has chosen one.
    """
    state = _read_state(_player_path(world_id, player_id, save_dir))
    if state is None or state.get("version") != SAVE_VERSION:
        return None
    try:
        player = state["player"]
        item_count = (
            len(player["inventory"])
            + (player["main_hand"] is not None)
            + (player["off_hand"] is not None)
        )
        return {
            "name": player["name"],
            "player_class": player["player_class"],
            "level": player["level"],
            "xp": player["xp"],
            "hp": player["hp"],
            "max_hp": player["max_hp"],
            "dungeon_level": player["dungeon_level"],
            "max_dungeon_level": MAX_DUNGEON_LEVEL,
            "item_count": item_count,
        }
    except (KeyError, TypeError):
        return None


def delete_save(world_id: str, player_id: str, save_dir: Path | None = None) -> None:
    """Delete only this player's save. world.json survives - others may still use it."""
    _player_path(world_id, player_id, save_dir).unlink(missing_ok=True)
