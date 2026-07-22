# Architecture

A module-by-module map of how the game works today, for orientation before
making changes. Not a changelog — see `ROADMAP.md` for what's shipped and
planned.

## Two front ends, one engine

`__main__.py` (CLI, a plain `input()`/`print()` loop) and `web/server.py`
(FastAPI + WebSocket) are both thin drivers around the same `Game` class in
`game.py`. Neither has any game logic of its own — the CLI has no
persistence at all, and `server.py` only adds the connection/session
handshake around `Game`.

## `Game` (`game.py`) — the orchestrator, not the rule-keeper

Owns `player` (a `Player`), `rooms` (dict of `Room`), `coords`, and
`output`. Its methods (`move`, `attack`, `take`, `cast`, etc.) don't
implement rules themselves — they call into the mechanics modules below,
then narrate the result via `self.emit(...)` (appends to `output`, records
history). `status()` is the one method that builds the JSON snapshot the
web sidebar and the 2D map both consume.

## Mechanics modules — pure functions + result objects

`combat.py`, `leveling.py`, `inventory.py`, `skills.py`. Each takes
`Player`/`Room`/`Monster` objects, mutates them in place, and returns a
small dataclass (`AttackResult`, `LevelUp`, `TakeResult`, `UseResult`)
describing what happened. `Game` narrates that result into player-facing
text. This split is why UI-facing work (the 2D map, the world-select
screen) has never needed to touch combat.

## Data models (`models/`)

`Player`, `Room`, `Item`, `Monster` — plain dataclasses, no behavior.

## Content templates (`templates/`)

Static game content as frozen dataclass lists — `classes.py`,
`monsters.py`, `bosses.py`, `items.py` (7 weapon/off-hand tiers × 4
classes), `rooms.py`, `skills.py`, `worlds.py`. Each has a `_TEMPLATES`
list and usually a `..._template_for(...)` lookup.

## `world.py` — dungeon generation

`generate_dungeon()` grows a self-avoiding random tree of rooms on a grid,
places the boss farthest from the entrance, attaches a vault beyond it
(crown only for the final boss; every other boss's vault just
`auto_advance`s to the next dungeon), and scatters monsters/items on the
rest.

## `commands.py`

The verb dispatch table (`COMMANDS` dict) — parses a raw command string and
calls the matching `Game` method. This is the single seam both the CLI and
the web client share.

## `minimap.py`

`compute_coords` (BFS over `Room.exits` for grid positions), `render_map`
(ASCII minimap), and `room_snapshots` (the structured per-room data —
position, monster, items — that feeds the 2D tile canvas). All three agree
on the same "known" room set (visited rooms plus their immediate
neighbors), so the fog-of-war rule can't drift between renderers.

## `persistence.py`

Serializes/deserializes a whole `Game` (player + rooms) to JSON, keyed by
`(world_id, player_id)` at `<save_dir>/<world_id>/<player_id>.json`.
Stamped with `SAVE_VERSION`; a mismatch discards the save rather than
risking a crash on an incompatible shape.

## Web layer

`server.py` handles one `/ws` connection: sets a `player_id` cookie on
first visit, then every connection goes world-select → (resume an existing
save, or class-select → name-select for a new one) → a plain
command/response loop, saving after every turn. `static/app.js` renders
`status()` into the sidebar (stats, equipment, skills, inventory) and draws
the room map on `<canvas>` using sprites in `static/tiles/` (a CC0
tileset), instead of ASCII text.

## Not built yet

Multiplayer/shared-world state — each world is still solo-per-player;
design is written up in `MULTIPLAYER-DESIGN.md` but not implemented. 2D
graphics polish (animation, autotiling, per-item icons) is deferred, see
`2D-GRAPHICS-PLAN.md` and `ROADMAP.md`.
