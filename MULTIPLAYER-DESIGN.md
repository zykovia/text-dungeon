# Design: Multiplayer shared dungeon

Not implemented yet. This is the "own design pass before implementation
starts" the roadmap's design note calls for, written down so it doesn't have
to be re-derived. Covers the shared-dungeon and persistent-world roadmap
items together, since they're the same architectural pivot.

## Locked decision: persistent per-level dungeons

Today, defeating a boss regenerates a brand-new, larger dungeon and moves
that one player into it (`dungeon_level` lives on `Player`, rooms are
regenerated and owned by `Game`). In a shared world that can't work as-is:
regenerating a level would wipe it out from under any other player still
standing in it.

Chosen approach: the world keeps every dungeon level's rooms alive once
generated, in a dict of `level -> rooms`, never discarded. Killing a boss
only reveals the next level for whoever did it; players in the same world can
be on different levels at once, each level still fully shared by whoever's
there. No mass "everyone gets teleported" event, no broadcast needed for
advancing specifically — only the advancing player's own session is
affected.

## Data model split

Today `Game` conflates two things that need to become separate: one
player's session, and the dungeon's actual state. The split:

- **`World`** (new, one per `world_id`, shared by every player in it):
  owns `levels: dict[int, dict[str, Room]]`. A level is generated lazily
  the first time anyone reaches it (via the existing `generate_dungeon`,
  scaled by that level the same way `Game._enter_new_dungeon` does today),
  then persists — monsters take damage, get killed, items get taken, and
  none of that resets unless the whole world is reset by choice.
- **`Player`**: unchanged. Still owns `dungeon_level`, `current_room`,
  `visited`, inventory, equipment, XP. Looks up its current room set as
  `world.levels[player.dungeon_level]` instead of that dict being owned
  directly by whatever object is running the session.
- **Session** (was `Game`): still the per-connection object that narrates
  outcomes via `emit`/`output`, but its "rooms" become a lookup into the
  shared `World` rather than something it owns and regenerates itself.

## Boss kill / advance

`player.dungeon_level += 1`, then fetch (or lazily generate, if this is the
first player ever to reach it) `world.levels[new_level]`, relocate only that
player to its entrance. Everyone else, on any other level, is untouched.

Two players reaching a new level for the first time at nearly the same
moment is the one race worth naming explicitly: "is level N+1 already
generated?" must be checked and, if not, generated-and-stored as one
uninterrupted synchronous step (see Concurrency below for why this is safe
without an explicit lock, given the single-process constraint).

## Death / respawn changes

A real, necessary behavior change: dying no longer rerolls the dungeon.
Respawn becomes "teleport back to the entrance of your current level's
already-existing rooms, full heal, keep inventory/level/XP" — not "generate
a fresh layout." A side effect worth calling out rather than treating as
incidental: monsters you've already killed and items you've already taken on
that level stay killed/taken after you respawn, since the level isn't
regenerated. The world gets easier as it's played, which is the right feel
for something persistent and shared, but is a genuine change from solo
play's "every death is a fresh dungeon" today.

## Shared combat and items

`Room.monster` becomes one object any player currently in that room can
attack; whoever lands the killing blow gets the XP, individually, same as
today. `Room.items` stays first-take-wins, already atomic. Two players in
the same room simultaneously fighting the same monster, or racing for the
same item, is the intended shared-dungeon experience, not an edge case to
prevent.

## Concurrency: why no locks, and the one constraint that buys it

The obvious worry — two players attacking the same monster "at the same
time" — turns out not to need explicit locking, on one condition: **this
stays a single-process deployment** (true today; nothing in the
`Dockerfile`/`docker-compose.yml` sets multiple uvicorn workers). Python's
asyncio event loop is single-threaded and cooperative: two coroutines can
only interleave at an `await` point. None of the mutation code
(`combat.py`, `inventory.py`, the `World`'s lazy level-generation) has an
`await` anywhere inside it, so one player's `attack()` runs to completion
uninterrupted before the event loop can even look at another connection's
message. That serializes every shared-state mutation for free.

The constraint this imposes going forward: never put an `await` inside
game-mutation logic, and never scale this past one worker process without
first redesigning state storage (e.g. an external store like Redis, with
real locking) — horizontal scaling is explicitly out of scope for this
design.

## Broadcast layer

The genuinely new piece of infrastructure. Today's model is pure
request/response: one command in, one response out, to that same
connection — there's no way for Player B to learn that Player A just fought
the monster in their shared room. Needed:

- An in-memory connection registry in `server.py`:
  `world_id -> {player_id: websocket}`, populated on connect (after
  world-select) and cleaned up on disconnect.
- After any room-mutating command, fan out a short narrated line (e.g. "A
  Ranger attacks the goblin.") to other connections currently in that
  *same room* (matched by `current_room` + `dungeon_level`) — scoped to the
  room, not the whole world, so it isn't noisy for players elsewhere.
- Since everything runs on one event loop, this is just direct
  `await other_ws.send_json(...)` calls made from inside the acting
  player's own command handler. No pub/sub broker needed.

## Persistence reshape

Rooms move out of the per-player save file entirely. New layout:

- `<save_dir>/<world_id>/world.json` — `{"levels": {"1": {room_id: ...},
  "2": {...}}}`, shared, one file per world.
- `<save_dir>/<world_id>/players/<player_id>.json` — just the `Player`
  dataclass fields (no rooms), smaller than today's save and no longer
  duplicated per player.

This is a genuine schema change (unlike the world-select work, which only
changed *where* a save lived, not *what* was in it) — it warrants a
`SAVE_VERSION` bump this time. Existing saves get discarded on load, same as
every prior version bump.

An in-memory `dict[str, World]` cache on the server (populated from
`world.json` on first access, not reloaded from disk per request) lets every
concurrently-connected player in the same world share the exact same Python
`World` object, which is what makes the broadcast/shared-state model work at
all.

## File-by-file sketch (for the eventual implementation pass)

- **`world_state.py`** (new): `World` class holding `levels`, plus a
  `level_rooms(level, player_class, upgrade context)` method that generates
  and caches a level on first request.
- **`game.py`**: `Game`'s `self.rooms` stops being owned directly; becomes a
  lookup into `self.world.levels[self.player.dungeon_level]`.
  `_enter_new_dungeon`/`respawn`/`advance` change per the sections above.
- **`persistence.py`**: split into world-state save/load and player-state
  save/load as separate files; `SAVE_VERSION` bump.
- **`server.py`**: add the `dict[str, World]` world cache and the
  `world_id -> {player_id: websocket}` connection registry; `play()` looks
  up/creates the shared `World` before wiring a session against it, and
  fans out room-scoped narration after mutating commands.
- **`combat.py`/`inventory.py`/`skills.py`**: unchanged. These were already
  pulled out as pure functions over `Player`/`Room`/`Monster` earlier this
  session, specifically so `game.py` narrates instead of also implementing
  — that split pays off directly here, since none of them assume a
  single-owner `Game`.

## Non-goals

- Horizontal scaling / multiple worker processes (single-process is a load-
  bearing assumption of the concurrency argument above, not an incidental
  detail).
- Player-vs-player interaction. Still purely incidental co-op: same
  monster, same items, no combat between players.
- Chat/presence narration beyond the minimal room-scoped combat line above.
  Full presence/chat stays its own "Other ideas raised" item.
- Any fairness/turn-ordering system for simultaneous kills. First
  synchronous command to land the killing blow wins; ties are broken by
  event-loop scheduling order, which is fine at this scale.
- Migrating existing single-player saves into the new world/player split
  (the `SAVE_VERSION` bump discards them, as usual).
