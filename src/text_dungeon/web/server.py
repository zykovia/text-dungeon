from __future__ import annotations

import uuid
from pathlib import Path

from fastapi import Cookie, FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from ..character import default_name_for_class
from ..game import Game
from ..persistence import delete_save, load_player, load_summary, load_world, save_player, save_world
from ..templates import CLASS_TEMPLATES, WORLD_TEMPLATES
from ..world_state import World

STATIC_DIR = Path(__file__).parent / "static"
PLAYER_ID_COOKIE = "player_id"
PLAYER_ID_COOKIE_MAX_AGE = 60 * 60 * 24 * 365

app = FastAPI(title="Text Dungeon")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# One shared World per world_id, kept in memory for the life of the process so
# every concurrently-connected player in the same world mutates the same
# in-memory rooms/monsters - this is what makes "shared" actually visible.
worlds: dict[str, World] = {}
# world_id -> {player_id: (websocket, Game)}, for room-scoped broadcast.
world_sessions: dict[str, dict[str, tuple[WebSocket, Game]]] = {}


def _get_world(world_id: str) -> World:
    if world_id not in worlds:
        worlds[world_id] = load_world(world_id) or World()
    return worlds[world_id]


def _player_ids_in_room(
    sessions: dict[str, tuple[WebSocket, Game]],
    dungeon_level: int,
    room_id: str,
    exclude_player_id: str,
) -> list[str]:
    """Who's literally standing in this exact room right now.

    Stricter than _player_ids_who_know_room: used for chat, where "you can
    see this room on your map" shouldn't mean "you can overhear it."
    """
    return [
        player_id
        for player_id, (_, other_game) in sessions.items()
        if player_id != exclude_player_id
        and other_game.player.dungeon_level == dungeon_level
        and other_game.player.current_room == room_id
    ]


def _player_ids_who_know_room(
    sessions: dict[str, tuple[WebSocket, Game]],
    dungeon_level: int,
    room_id: str,
    exclude_player_id: str,
) -> list[str]:
    """Anyone whose own fog-of-war reveals this room, used for combat/presence."""
    return [
        player_id
        for player_id, (_, other_game) in sessions.items()
        if player_id != exclude_player_id and other_game.knows_room(dungeon_level, room_id)
    ]


def _status_with_players(
    game: Game, sessions: dict[str, tuple[WebSocket, Game]], exclude_player_id: str
) -> dict:
    """game.status(), with each room's "players" list of who else is standing there.

    exclude_player_id must be whoever this status is *for* (so they don't see
    themselves in their own room's list), not the player who triggered
    whatever event caused this status to be sent.
    """
    status = game.status()
    for room_id, room in status["rooms"].items():
        present = _player_ids_in_room(sessions, game.player.dungeon_level, room_id, exclude_player_id)
        room["players"] = [
            {
                "name": sessions[pid][1].player.name,
                "player_class": sessions[pid][1].player.player_class,
            }
            for pid in present
        ]
    return status


def _mark_pending(
    pending: dict[str, list[str]], player_ids: list[str], message: str | None = None
) -> None:
    for player_id in player_ids:
        lines = pending.setdefault(player_id, [])
        if message:
            lines.append(message)


async def _flush(sessions: dict[str, tuple[WebSocket, Game]], pending: dict[str, list[str]]) -> None:
    for player_id, lines in pending.items():
        if player_id not in sessions:
            continue
        other_ws, other_game = sessions[player_id]
        try:
            await other_ws.send_json(
                {
                    "lines": lines,
                    "status": _status_with_players(other_game, sessions, player_id),
                    "game_over": False,
                }
            )
        except Exception:
            # Best-effort: a recipient whose own connection is already
            # dropping shouldn't prevent delivering to everyone else.
            pass


@app.get("/")
async def index(player_id: str | None = Cookie(default=None)) -> FileResponse:
    response = FileResponse(STATIC_DIR / "index.html")
    if player_id is None:
        response.set_cookie(
            PLAYER_ID_COOKIE,
            str(uuid.uuid4()),
            max_age=PLAYER_ID_COOKIE_MAX_AGE,
            httponly=True,
            samesite="lax",
        )
    return response


async def _choose_world(websocket: WebSocket, player_id: str | None) -> str:
    await websocket.send_json(
        {
            "type": "world_select",
            "options": [
                {
                    "id": t.id,
                    "name": t.name,
                    "description": t.description,
                    "character": load_summary(t.id, player_id) if player_id else None,
                }
                for t in WORLD_TEMPLATES
            ],
        }
    )
    choice = (await websocket.receive_text()).strip()
    return next(
        (
            t.id
            for t in WORLD_TEMPLATES
            if t.id == choice or t.name.lower() == choice.lower()
        ),
        WORLD_TEMPLATES[0].id,
    )


async def _choose_class(websocket: WebSocket) -> str:
    await websocket.send_json(
        {
            "type": "class_select",
            "options": [
                {"name": t.name, "description": t.description} for t in CLASS_TEMPLATES
            ],
        }
    )
    choice = (await websocket.receive_text()).strip()
    return next(
        (t.name for t in CLASS_TEMPLATES if t.name.lower() == choice.lower()),
        CLASS_TEMPLATES[0].name,
    )


async def _choose_name(websocket: WebSocket, player_class: str) -> str:
    default_name = default_name_for_class(player_class)
    await websocket.send_json({"type": "name_select", "default": default_name})
    name = (await websocket.receive_text()).strip()
    return name or default_name


async def _resume_or_start(
    websocket: WebSocket, world_id: str, player_id: str | None, world: World
) -> Game:
    if player_id is not None:
        try:
            saved = load_player(world_id, player_id)
        except (OSError, ValueError, KeyError):
            saved = None
        if saved is not None:
            player, running = saved
            if running:
                game = Game(player=player, world=world, running=running)
                game.emit("Welcome back. Here's what's happened in this dungeon so far:")
                game.output.extend(game.current_dungeon_history())
                game.look()
                return game
    player_class = await _choose_class(websocket)
    player_name = await _choose_name(websocket, player_class)
    game = Game(player_class=player_class, player_name=player_name, world=world)
    game.intro()
    return game


@app.websocket("/ws")
async def play(websocket: WebSocket, player_id: str | None = Cookie(default=None)) -> None:
    await websocket.accept()
    world_id = await _choose_world(websocket, player_id)
    world = _get_world(world_id)
    game = await _resume_or_start(websocket, world_id, player_id, world)
    player_id = player_id or str(uuid.uuid4())

    sessions = world_sessions.setdefault(world_id, {})
    sessions[player_id] = (websocket, game)

    try:
        await websocket.send_json(
            {
                "lines": game.pop_output(),
                "status": _status_with_players(game, sessions, player_id),
                "game_over": False,
            }
        )
        save_world(world_id, world)
        save_player(world_id, player_id, game.player, game.running)

        # Arrival: let anyone who can already see this room know we're here.
        arrival_pending: dict[str, list[str]] = {}
        _mark_pending(
            arrival_pending,
            _player_ids_who_know_room(
                sessions, game.player.dungeon_level, game.player.current_room, player_id
            ),
            f"{game.player.name} enters the room.",
        )
        await _flush(sessions, arrival_pending)

        while True:
            command = (await websocket.receive_text()).strip()
            if command:
                before = (game.player.dungeon_level, game.player.current_room)
                game.handle_command(command)
                if not game.player.alive:
                    game.emit("")
                    game.emit("You have died.")
                    game.respawn()
                after = (game.player.dungeon_level, game.player.current_room)

                pending: dict[str, list[str]] = {}
                if game.last_broadcast:
                    level, room_id, message = game.last_broadcast
                    game.last_broadcast = None
                    _mark_pending(
                        pending, _player_ids_who_know_room(sessions, level, room_id, player_id), message
                    )
                if game.last_chat:
                    level, room_id, message = game.last_chat
                    game.last_chat = None
                    _mark_pending(
                        pending, _player_ids_in_room(sessions, level, room_id, player_id), message
                    )
                if before != after:
                    before_level, before_room = before
                    after_level, after_room = after
                    _mark_pending(
                        pending,
                        _player_ids_who_know_room(sessions, before_level, before_room, player_id),
                        f"{game.player.name} leaves the room.",
                    )
                    _mark_pending(
                        pending,
                        _player_ids_who_know_room(sessions, after_level, after_room, player_id),
                        f"{game.player.name} enters the room.",
                    )
                await _flush(sessions, pending)

            game_over = not game.running
            await websocket.send_json(
                {
                    "lines": game.pop_output(),
                    "status": _status_with_players(game, sessions, player_id),
                    "game_over": game_over,
                }
            )
            if game_over:
                delete_save(world_id, player_id)
                break
            save_world(world_id, world)
            save_player(world_id, player_id, game.player, game.running)
    except WebSocketDisconnect:
        pass
    finally:
        # Departure: remove our own session *first*, so the statuses built
        # for everyone else no longer include us, then let anyone who could
        # see us know we're gone.
        sessions.pop(player_id, None)
        departure_pending: dict[str, list[str]] = {}
        _mark_pending(
            departure_pending,
            _player_ids_who_know_room(
                sessions, game.player.dungeon_level, game.player.current_room, player_id
            ),
            f"{game.player.name} leaves the room.",
        )
        await _flush(sessions, departure_pending)


def main() -> None:
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
