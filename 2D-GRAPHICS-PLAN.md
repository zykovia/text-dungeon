# Approach: 2D graphics with stock assets

Not committed to, not scheduled. A phased approach for turning the web client
from a text log into a 2D tile map, written down so the design doesn't have to
be re-derived later.

## What's already in place

- `minimap.py` derives grid coordinates for every room by walking cardinal
  `exits` from the entrance (`compute_coords`), and `game.py` recomputes
  `self.coords` on load/generation. There's no schema change needed to get
  spatial data, just a new place to expose it.
- `status()` currently exposes the map only as pre-rendered ASCII
  (`map_lines`). Monster/item presence per room is narrated as text, not
  structured, in the WebSocket `lines` payload.
- The web sidebar already has a dedicated map area (`#map-display` in
  `web/static/app.js`), so swapping its content model from text to canvas is a
  contained change, not a layout redesign.

## Recommendation

Stay inside the existing FastAPI + WebSocket + vanilla-JS client
(`web/server.py`, `web/static/app.js`); no new framework needed. Keep the
server as the authoritative text/state engine and treat this purely as a
rendering-layer addition on the client. The CLI is unaffected throughout.

## Non-goals

- No CLI changes; text mode stays exactly as it is.
- No changes to `combat.py` or `skills.py`. Combat stays turn-based and
  narrated via `attack`/`cast` commands; the room is just illustrated now.
- No persistence format changes. Coordinates are already recomputed from
  `rooms`/`exits` on every load, never stored, and that stays true.
- No real spatial movement/positioning within a room. That's a much bigger
  design pass (would touch `combat.py`, `skills.py`, and the room model
  itself) and isn't needed to get "2D with stock graphics."

## Phases

**Phase 0: Pick the stack and assets, no code.**
Pick one stock tileset with everything needed in one style (e.g. Kenney.nl's
dungeon/roguelike packs, CC0) and a fixed tile size (16 or 32px). Add a
`<canvas>` in place of the current `#map-display` div.

**Phase 1: Expose spatial + entity data in `status()`.**
Add a `rooms` field to `Game.status()` built from `self.coords` plus each
room's `monster`/`items`/`exits`, scoped to the same "known" set
`render_map` already computes (visited rooms + their immediate neighbors) so
the client isn't handed the whole unexplored dungeon. Keep `map_lines`
as-is; this is additive, zero risk to text mode.

**Phase 2: Static grid renderer, no art yet.**
New JS module draws a rect per known room from `status.rooms`: lit for
visited, dim for known-but-unvisited, highlighted for current. Functionally
the ASCII map redrawn in pixels; proves the coordinate pipeline end to end
before any art is involved.

**Phase 3: Swap rects for tileset sprites.**
Load the tile atlas, draw floor/wall tiles per cell instead of colored rects,
connectors between rooms that have exits to each other.

**Phase 4: Entity sprites.**
Draw the player's class sprite on the current-room tile, a monster icon on
any known room with a live `monster`, an item icon on any with `items`.

**Phase 5 (stretch): motion polish.**
Slide/hop animation between tiles on `move`, a flash/shake on `attack`
resolution. Cosmetic only; underlying state transitions stay discrete
per-command, not real-time.
