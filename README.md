# Text Dungeon

A small text-based dungeon crawler written in Python.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Play

```bash
python -m text_dungeon
# or, after install:
text-dungeon
```

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
