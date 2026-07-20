from __future__ import annotations

import dataclasses
import json
import os
from pathlib import Path

from .game import Game
from .models import Item, Monster, Player, Room

# Bump this whenever a save produced by an older version of the game could crash
# or misbehave on load (e.g. a Player/Room field is added, renamed, or removed,
# or dungeon generation changes in a way old saves shouldn't carry forward).
# Saves tagged with a different version are discarded instead of being loaded.
SAVE_VERSION = 4


def default_save_dir() -> Path:
    configured = os.environ.get("TEXT_DUNGEON_SAVE_DIR")
    return Path(configured) if configured else Path.home() / ".text_dungeon" / "saves"


def _save_path(player_id: str, save_dir: Path | None) -> Path:
    return (save_dir or default_save_dir()) / f"{player_id}.json"


def _state_from_game(game: Game) -> dict:
    return {
        "version": SAVE_VERSION,
        "player": dataclasses.asdict(game.player) | {"visited": sorted(game.player.visited)},
        "rooms": {room_id: dataclasses.asdict(room) for room_id, room in game.rooms.items()},
        "running": game.running,
    }


def _game_from_state(state: dict) -> Game:
    player_data = dict(state["player"])
    player_data["inventory"] = [Item(**item) for item in player_data["inventory"]]
    player_data["main_hand"] = (
        Item(**player_data["main_hand"]) if player_data["main_hand"] is not None else None
    )
    player_data["off_hand"] = (
        Item(**player_data["off_hand"]) if player_data["off_hand"] is not None else None
    )
    player_data["visited"] = set(player_data["visited"])
    player = Player(**player_data)

    rooms = {}
    for room_id, room_data in state["rooms"].items():
        room_data = dict(room_data)
        room_data["items"] = [Item(**item) for item in room_data["items"]]
        room_data["monster"] = (
            Monster(**room_data["monster"]) if room_data["monster"] is not None else None
        )
        rooms[room_id] = Room(**room_data)

    return Game(player=player, rooms=rooms, running=state["running"])


def save_game(player_id: str, game: Game, save_dir: Path | None = None) -> None:
    path = _save_path(player_id, save_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(_state_from_game(game)))


def load_game(player_id: str, save_dir: Path | None = None) -> Game | None:
    path = _save_path(player_id, save_dir)
    if not path.exists():
        return None
    state = json.loads(path.read_text())
    if state.get("version") != SAVE_VERSION:
        path.unlink(missing_ok=True)
        return None
    return _game_from_state(state)


def delete_save(player_id: str, save_dir: Path | None = None) -> None:
    _save_path(player_id, save_dir).unlink(missing_ok=True)
