from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from ..game import Game

STATIC_DIR = Path(__file__).parent / "static"

app = FastAPI(title="Text Dungeon")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
async def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.websocket("/ws")
async def play(websocket: WebSocket) -> None:
    await websocket.accept()
    game = Game()
    game.intro()
    await websocket.send_json({"lines": game.pop_output(), "game_over": False})

    try:
        while True:
            command = (await websocket.receive_text()).strip().lower()
            if command:
                game.handle_command(command)

            game_over = not game.running or not game.player.alive
            if not game.player.alive:
                game.emit("")
                game.emit("You have died. Game over.")

            await websocket.send_json({"lines": game.pop_output(), "game_over": game_over})
            if game_over:
                break
    except WebSocketDisconnect:
        pass


def main() -> None:
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
