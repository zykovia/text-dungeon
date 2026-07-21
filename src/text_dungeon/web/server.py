from __future__ import annotations

import uuid
from pathlib import Path

from fastapi import Cookie, FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from ..character import default_name_for_class
from ..game import Game
from ..persistence import delete_save, load_game, load_summary, save_game
from ..templates import CLASS_TEMPLATES, WORLD_TEMPLATES

STATIC_DIR = Path(__file__).parent / "static"
PLAYER_ID_COOKIE = "player_id"
PLAYER_ID_COOKIE_MAX_AGE = 60 * 60 * 24 * 365

app = FastAPI(title="Text Dungeon")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


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


async def _resume_or_start(websocket: WebSocket, world_id: str, player_id: str | None) -> Game:
    if player_id is not None:
        try:
            saved = load_game(world_id, player_id)
        except (OSError, ValueError, KeyError):
            saved = None
        if saved is not None and saved.running:
            saved.emit("Welcome back. Here's what's happened in this dungeon so far:")
            saved.output.extend(saved.current_dungeon_history())
            saved.look()
            return saved
    player_class = await _choose_class(websocket)
    player_name = await _choose_name(websocket, player_class)
    game = Game(player_class=player_class, player_name=player_name)
    game.intro()
    return game


@app.websocket("/ws")
async def play(websocket: WebSocket, player_id: str | None = Cookie(default=None)) -> None:
    await websocket.accept()
    world_id = await _choose_world(websocket, player_id)
    game = await _resume_or_start(websocket, world_id, player_id)
    player_id = player_id or str(uuid.uuid4())

    await websocket.send_json(
        {"lines": game.pop_output(), "status": game.status(), "game_over": False}
    )
    save_game(world_id, player_id, game)

    try:
        while True:
            command = (await websocket.receive_text()).strip().lower()
            if command:
                game.handle_command(command)
                if not game.player.alive:
                    game.emit("")
                    game.emit("You have died.")
                    game.respawn()

            game_over = not game.running
            await websocket.send_json(
                {"lines": game.pop_output(), "status": game.status(), "game_over": game_over}
            )
            if game_over:
                delete_save(world_id, player_id)
                break
            save_game(world_id, player_id, game)
    except WebSocketDisconnect:
        pass


def main() -> None:
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
