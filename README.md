# Text Dungeon

A small text-based dungeon crawler written in Python. Play it in a terminal,
or as a browser game served over WebSocket.

Each run generates a fresh, randomly laid-out dungeon (6-10 rooms), so no two
playthroughs are the same. Defeating monsters earns experience; reaching 10 XP
levels you up (+5 max HP, full heal). Dying doesn't end the game: you wake up
at the entrance of a brand new dungeon, keeping your inventory, level, and XP.

Defeating the boss and taking the crown descends you into a new dungeon too,
2 rooms larger (both min and max) than the one before, keeping your gear,
level, and XP. This happens up to 7 dungeons deep; the 7th holds the Dungeon
Emperor, a much tougher super boss. Defeat it and take its crown to win the
game for good.

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

## Play with others on your WiFi

The server already binds to all interfaces, so anyone on your local network
can join once the container is running, you just need to hand them a URL.
`scripts/play.sh` does this for you: it builds and starts the container, then
prints a shareable LAN URL and a scannable QR code (via `qrencode` if
installed, e.g. `brew install qrencode`, otherwise a plain URL).

```bash
./scripts/play.sh
```

Point phones/laptops on the same WiFi at the printed `http://<your-ip>:8000`
(or the `.local` Bonjour address on Apple devices). Press Ctrl+C to stop and
tear down the container.

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

- `go <direction>` / `n` / `s` / `e` / `w`: move
- `look`: describe the current room
- `take <item>`: pick up an item
- `inventory` / `i`: show your inventory
- `attack`: fight the monster in the room
- `use <item>`: use an item (e.g. drink a potion)
- `map` / `m`: show a minimap of the rooms you've explored
- `help`: list commands
- `quit`: leave the dungeon

## Tests

```bash
pytest
```
