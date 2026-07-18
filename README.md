# Text Dungeon

A small text-based dungeon crawler written in Python. Play it in a terminal,
or as a browser game served over WebSocket.

## Play in the browser (Docker)

```bash
docker compose up --build
```

Then open http://localhost:8000 in a browser. Each browser tab gets its own
independent game (a fresh `Game` per WebSocket connection); refreshing the
page starts a new run.

Without Compose:

```bash
docker build -t text-dungeon .
docker run --rm -p 8000:8000 text-dungeon
```

## Setup (local development)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Play in a terminal

```bash
python -m text_dungeon
# or, after install:
text-dungeon
```

## Play in the browser (without Docker)

```bash
text-dungeon-web
```

Then open http://localhost:8000.

## Commands

- `go <direction>` / `n` / `s` / `e` / `w` — move
- `look` — describe the current room
- `take <item>` — pick up an item
- `inventory` / `i` — show your inventory
- `attack` — fight the monster in the room
- `use <item>` — use an item (e.g. drink a potion)
- `help` — list commands
- `quit` — leave the dungeon

## Tests

```bash
pytest
```
