# Approach: first-person view for the web client

Not committed to, not scheduled. A phased approach for turning the web
client's room view into a first-person (Wizardry/Dungeon Master/Legend of
Grimrock-style) viewport, written down so the design doesn't have to be
re-derived later.

## What's already in place

- `Room.exits` is keyed by cardinal direction (`north`/`south`/`east`/
  `west`), and `minimap.compute_coords()` already derives a planar `(x, y)`
  grid for every room by walking those exits from the entrance
  (`directions.py`'s `DIRECTION_DELTAS`). The dungeon is already laid out on
  exactly the grid a first-person view needs; there's no dungeon-model or
  generation change required to get spatial data.
- The 2D tile map (`2D-GRAPHICS-PLAN.md`, shipped) already renders per-room
  sprites from `status()`'s `rooms` field, scoped to the same fog-of-war
  `known_room_ids` used everywhere else. That data feed is reused as-is;
  this plan only adds a different way to draw it.
- Movement today is absolute (`go north`), with no concept of which way the
  player is currently looking. First-person needs that concept; nothing
  currently tracks it.

## Recommendation

Stay inside the existing FastAPI + WebSocket + vanilla-JS client; no new
framework, no raycasting engine. Add a `facing` direction to `Player` and a
small set of relative movement commands, then render the current room as a
static corridor frame (front/left/right/back derived from `exits` relative
to `facing`) with the room's own tile sprites billboarded into it, the same
way Dungeon Master and early Wizardry render dungeons — not a true 3D/raycast
engine. This is a rendering-and-input-mode addition on top of the existing
model, not a replacement of it.

## Locked decisions

**Facing lives on `Player`, not on the dungeon.** A room's exits don't
change meaning; `facing` is purely "which of this room's existing exits is
currently 'ahead' for this one player." Two players in the same room can
face different directions independently.

**Absolute `go <direction>` stays.** It's not replaced by relative
movement, it's supplemented. The CLI keeps working exactly as it does today
with zero changes required; first-person is additive on the web client.
Relative commands (`turn left`/`turn right`/`move forward`/`move back`) are
implemented in the same command layer so both interfaces get them, but only
the web client's viewport actually depends on `facing`.

**No real 3D geometry or raycasting.** The renderer draws a fixed corridor
frame per facing state (open archway or wall tile in front/left/right/back,
based on which cardinal exits exist relative to `facing`) and billboards
sprites into it — this room's monster/items in the foreground, optionally a
peek of what's directly ahead. This keeps the same flat tile-sprite assets
already in `web/static/tiles/` instead of requiring new art or a 3D pipeline.

**The 2D top-down map isn't replaced, it's demoted to an inset.** Losing
spatial orientation is the classic complaint about pure first-person
dungeon crawlers; Grimrock and its predecessors all solve it with a
persistent minimap corner. The existing canvas map becomes that inset with
no changes to its own data feed or fog-of-war rule.

**Room-scoped presence rules don't change.** `_player_ids_in_room` already
means "who renders as physically here"; that's exactly the set that needs a
first-person billboard. `_player_ids_who_know_room` (fog-of-war) stays a
minimap-only concern, not a first-person-viewport concern — a player merely
visible on the map isn't rendered in anyone's corridor view. No new
broadcast plumbing needed in `web/server.py`.

## Data model changes

- `Player` gains `facing: str = "north"`.
- New commands (`commands.py`): `turn left`, `turn right` (rotate `facing`
  through `north → east → south → west → north`, no round cost, no
  broadcast — purely local orientation), `move forward` / `move back`
  (resolve to the same room-transition path `go <direction>` already uses,
  just deriving the direction from `facing` instead of taking it literally).
- `status()` gains a `facing` field alongside the existing per-player state.

## Phases

**Phase 0: Pick corridor-frame art, no code.**
Decide what a "wall ahead", "open archway ahead", "wall to the left/right",
"open exit to the left/right" look like using the existing 0x72 tileset (or
a small supplemental set if the existing tiles don't have wall-facing
pieces). Fixed frame size, no perspective/vanishing-point art needed for a
first pass — flat billboards, like Dungeon Master.

**Phase 1: `facing` + relative commands, server-only.**
Add the field and the three new commands, unit-testable with zero rendering
work: `turn left`/`turn right` cycle `facing` correctly, `move forward`/
`move back` move the player exactly like the equivalent `go <direction>`
would. CLI and web both get this for free since it's in the shared command
layer; nothing in the CLI's text output needs to change to support it.

**Phase 2: Static first-person renderer, current room only.**
New canvas view in `app.js` driven by `status()`: draws the fixed corridor
frame for the room's exits relative to `facing`, billboards the current
room's monster/items in the foreground, billboards any other player
literally in the room (via the existing `players` roster already in each
room's status). No depth, no rooms-ahead peek yet — proves the facing/frame
pipeline end to end.

**Phase 3: Minimap inset + view toggle.**
Shrink the existing 2D map into a corner inset alongside the first-person
view. Add a client-side toggle to go full first-person or full top-down for
players who prefer the old view; both read the same `status()` payload, no
server changes.

**Phase 4 (stretch): One room of depth.**
If `exits[facing]` leads somewhere known, billboard that room's monster/
item as a smaller, farther-away sprite through the archway ahead, using the
same known-room data already available from fog-of-war. Still no real
geometry — just a second, smaller billboard layer.

**Phase 5 (stretch): Turn/move animation.**
Slide/rotate transition on `turn`/`move`, purely cosmetic. Underlying state
transitions stay discrete per-command, same as the 2D map's own Phase 5.

## Non-goals

- No raycasting engine, no true 3D geometry, no perspective-correct corridor
  art in the initial phases — flat billboards in a fixed frame.
- No changes to `combat.py`, `skills.py`, or targeting. A monster is still
  "the monster in this room"; first-person is a viewport change, not a
  positioning-within-a-room change.
- No CLI-visible behavior change. Relative movement commands exist in the
  shared command layer for consistency, but nothing about CLI output
  requires them and the CLI never renders a first-person view.
- No change to fog-of-war, broadcast, or presence rules in `server.py` —
  the existing `_player_ids_in_room` / `_player_ids_who_know_room` split
  already draws exactly the line first-person rendering needs.
- No persistence format changes beyond the one new `Player.facing` field
  (bump `SAVE_VERSION` when this actually ships, same as every prior
  `Player`-shape change).
