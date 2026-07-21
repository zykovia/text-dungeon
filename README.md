# Text Dungeon

A small text-based dungeon crawler written in Python. Play it in a terminal,
or as a browser game served over WebSocket.

Pick a class, Warrior, Ranger, Cleric, or Wizard, each with its own starting
HP, weapon, and set of skills/spells unlocked as you level up. Each run
generates a fresh, randomly laid-out dungeon (6-10 rooms), so no two
playthroughs are the same. Defeating monsters earns experience; reaching 10 XP
levels you up (+5 max HP, full heal). Dying doesn't end the game: you wake up
at the entrance of a brand new dungeon, keeping your class, gear, level, and
XP.

Defeating a dungeon's boss descends you into the next one, 2 rooms larger
(both min and max) than the one before, keeping your gear, level, and XP.
This happens up to 7 dungeons deep; the 7th holds the Dungeon Emperor, a much
tougher super boss guarding a golden crown. Defeat it and take the crown to
win the game for good.

## Play in the browser (Docker)

```bash
docker compose up --build
```

Then open http://localhost:8000 in a browser. Your first visit sets a
`player_id` cookie, then asks which world to play in (each world is an
independent, separately-saved dungeon) before dropping you into class and
name selection for a new game there. The server saves your progress to disk
after every command and resumes the same game (with a recap of what happened
in the current dungeon) whenever that browser reconnects to that world,
including after a server restart. The save is deleted once the game ends
(winning or quitting), so your next visit to that world starts a fresh run.

The sidebar's map panel renders the rooms you've explored as a small 2D tile
map (floor/wall tiles, your class's sprite, monsters, and items) instead of
plain ASCII, using a CC0 tileset (credited in
`src/text_dungeon/web/static/tiles/CREDITS.txt`).

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
- `inventory` / `i`: show what you're carrying and wielding
- `equip <item>`: wield an item from your inventory
- `unequip <item>`: put a wielded item back in your inventory
- `attack`: fight the monster in the room
- `use <item>`: use an item (e.g. drink a potion)
- `skills`: show the skills/spells you know
- `cast <skill>`: cast a known skill or spell (once per round)
- `map` / `m`: show a minimap of the rooms you've explored
- `history`: show everything you've done this playthrough
- `help`: list commands
- `quit`: leave the dungeon

## Tests

```bash
pytest
```

Or, with the `dev` extras installed (`pip install -e ".[dev]"`), run lint and
coverage together:

```bash
./scripts/check.sh
```
