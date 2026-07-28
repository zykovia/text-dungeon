# Approach: story and per-world narrative

Not committed to, not scheduled. A phased approach for adding a light
narrative layer on top of the existing RPG mechanics, written down so the
design doesn't have to be re-derived later.

## What's already in place

- `templates/worlds.py` already gives each world an id/name, used by the
  world-select screen. There's no per-world content beyond that identity
  today — every world draws from the same generic room-flavor pool.
- `templates/rooms.py` has 10 reusable flavor-text templates, picked
  procedurally by `world.py`'s `generate_dungeon()`. No NPCs exist anywhere
  in the model.
- `Room`/`Monster`/boss encounters already carry some flavor text, and the
  final boss's crown already functions as a de facto win condition.
- `game.py` has clear narration hookpoints already wired for other
  purposes — world entry, `descend`, and final-boss-win — where new story
  beats can be narrated without any new mechanics.
- `self.emit(...)` is the one narration path both the CLI and the web
  client already share, so anything narrated this way needs no front-end
  changes.

## Recommendation

Stay inside the existing engine; this is a content-and-narration-hooks
addition, not a new subsystem. No dialogue trees, no quest engine. Light
narrative layer: authored flavor text, static NPC lines, and a simple main
quest thread (defeat the world's final boss) told through story beats
instead of just "boss defeated" messaging.

Recommended sequencing relative to the other two plan docs in this repo:
this should land after `2D-GRAPHICS-PLAN.md` Phase 5 (small, already fully
scoped, makes the existing map feel alive first) and before
`FIRST-PERSON-PLAN.md` (the largest lift of the three, and least essential
to "feels like an adventure game with a story").

## Non-goals

- No dialogue trees or player choices that branch outcomes.
- No quest log or objectives UI.
- No changes to `combat.py`, `skills.py`, or `leveling.py`.
- No CLI changes beyond what it gets for free through `self.emit()`; no
  front-end framework change.
- No persistence format changes except the optional Phase 3 quest flag,
  which would bump `SAVE_VERSION` same as any other `Player`-shape change.

## Phases

**Phase 0: Write the content, no code.**
For each entry in `templates/worlds.py`, draft: a one-paragraph world intro
(shown on entry), 3-5 room-flavor variants themed to that world (replacing
the generic ones from `templates/rooms.py` for that world only), one
boss-encounter narrative beat, and a short victory beat for the crown/
final-boss win. Pure writing, reviewable before any code exists.

**Phase 1: NPCs as a new mechanics module.**
Add `templates/npcs.py` (frozen dataclass list, same pattern as
`templates/monsters.py`), a `dialogue.py` mechanics module (pure function +
result dataclass, same shape as `combat.py`/`inventory.py`), an `npc` field
on `Room` (`models/room.py`), and a `talk` verb in `commands.py`. Static
lines-only dialogue for this phase, no branching, no state. `Room.npc` can
be placed at generation time like monsters/items, so no `SAVE_VERSION`
bump is expected here.

**Phase 2: Wire per-world flavor into generation.**
`world.py`'s `generate_dungeon()` currently pulls from one shared
room-template pool; scope room/NPC selection to the world's own authored
set from Phase 0 instead. Narrate the Phase 0 world-intro/victory beats at
the existing world-entry and final-boss-win points in `game.py`.

**Phase 3 (stretch): a light quest flag.**
One boolean-ish milestone per world (e.g. "met the NPC who explains the
vault") surfaced back as flavor text later in the run, deliberately short
of a quest log or branching dialogue, per the light-narrative scope. The
only phase that needs a save-schema bump.
