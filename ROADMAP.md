# Roadmap

Requested future directions for Text Dungeon, in the order they were raised.

## Shipped

These were part of the roadmap discussion but have already been built:

- **Per-player session persistence.** A cookie-based `player_id` identifies a
  returning browser; the game is saved to disk after every turn and resumed
  on reconnect instead of restarting, including across server restarts.
- **Playthrough history.** Every line the player has seen is retained across
  respawns and dungeon advances. A `history` command replays the full
  playthrough; reconnecting recaps just the current dungeon.
- **Save version invalidation.** Saves are stamped with a version number; a
  save from an incompatible version is discarded (not resumed, not crashed
  on) so old cookies always land in a normal fresh game after a breaking
  change.
- **Room spacing fix.** Dungeon generation no longer allows two unconnected
  rooms to land grid-adjacent to each other, so the minimap never implies a
  connection that doesn't exist.
- **Character classes.** Players choose Warrior, Ranger, Cleric, or Wizard at
  the start of a run (a CLI menu or a web class-select screen), each with its
  own starting HP, attack, and starting weapon.
- **Class-specific items.** Weapon items are restricted to the class they're
  meant for; taking one as the wrong class is blocked and it stays in the
  room. Generic items (health potions, bandages) stay usable by everyone.
- **Equipment slots.** Combat bonuses come only from a `main_hand`/`off_hand`
  pair instead of summing every weapon ever carried. Each class starts with
  a matched pair (e.g. Warrior's rusty sword + wooden shield); `equip`/
  `unequip` swap gear in and out of the two slots, and off-hand items can
  either boost damage or reduce incoming damage.
- **Class skills and spells.** Each class has a themed set of four skills
  (Warrior: rally, shield bash, cleave, second wind; Ranger: quick shot,
  snare, evasion, precise strike; Cleric: heal, bless, divine shield, smite;
  Wizard: frost bolt, arcane shield, drain life, fireball), gated behind a
  per-class mana pool and unlocked progressively as the player levels up.
  `cast <skill>` applies a heal, an attack buff, a full block, or an enemy
  debuff that carries into the very next `attack`.
- **Weapon tiers.** Main-hand and off-hand items now come in 7 progressive
  tiers, with drops alternating between the two slots so gear upgrades stay
  balanced across a run.
- **Once-per-round skill lockout.** Skill effects are implemented behind an
  extensible interface, and a given skill can't be cast again until the next
  round, preventing spam of the strongest effect.
- **Item mechanics visible in UI.** Inventory and equip screens show each
  item's mechanical effect (damage, armor, healing) instead of just its name,
  so players can compare gear before equipping it.
- **Inventory decluttering.** Non-final dungeons no longer place a golden
  crown to collect; the vault beyond an ordinary boss auto-advances the
  player to the next dungeon on entry instead, so nothing piles up across
  the six regular dungeons. Only the true final boss still guards a crown to
  win. Weapons bumped out of a slot on `equip` are flagged retired and
  collapse into a single "Old gear (N)" line instead of cluttering the list
  one entry per obsolete tier.
- **Inventory/skills code split out of `game.py`.** `game.py` was mixing
  dungeon orchestration with the actual state mutation for items, equipment,
  and skills. That mechanics logic moved into `inventory.py` and `skills.py`,
  following the same pure-function-plus-result-object pattern already used
  by `combat.py`/`leveling.py`, so `game.py` now narrates outcomes instead of
  also implementing them. No behavior change.
- **Test coverage and dev tooling.** `inventory.py` and `skills.py` gained
  direct unit tests (mirroring the existing `test_combat.py`/
  `test_leveling.py` convention) covering every branch, bringing both
  modules to 100% coverage. Added `ruff` (lint) and `pytest-cov` (coverage)
  as dev dependencies, plus `scripts/check.sh` to run both in one command.
- **World select ingress (single-service version).** Players pick from a
  fixed catalog of worlds before entering the dungeon instead of always
  landing in one implicit world. The picker shows on every connection, no
  exceptions — an earlier version silently skipped it on a browser that had
  already picked before, which read as a bug (mobile always asked, desktop
  never did) rather than a convenience, so that shortcut was removed. Each
  world is an independently persisted save namespace
  (`<world_id>/<player_id>.json`); worlds the player already has a
  character in show that character's class, level, HP, dungeon floor, and
  item count right on the select screen, so they can recognize their own
  character before rejoining it. This is the player-facing half of the
  original design, built inside the one existing service: dungeons stay
  solo-per-player (no shared/concurrent state between players in a world
  yet) and there are no new containers. The multi-container routing part of
  the original design is still future work, noted below.
- **2D tile map (first increment).** The web sidebar's ASCII map now
  renders as a real tile map, using a CC0 tileset (0x72 DungeonTileset II):
  floor tiles, a class-matched player sprite on the current room, and
  monster/item sprites on known neighboring rooms, all drawn on a canvas
  scoped to the same fog-of-war rule the ASCII map already used. This
  covers Phases 1-4 of `2D-GRAPHICS-PLAN.md` in one pass. Deliberately out
  of scope: motion/animation (still Phase 5), true neighbor-aware
  autotiling (one flat wall tile fills every non-room cell instead of
  directional wall pieces), and per-exact-item-name icons (a three-way
  heal/crown/generic-weapon rule stands in for all ~58 named items).
- **Multiplayer shared dungeon.** Full write-up in `MULTIPLAYER-DESIGN.md`.
  Dungeons are now persistent per level within a world, shared by everyone
  who joins it: a level's rooms/monsters/items are generated once and never
  regenerated, so death/respawn no longer rerolls the dungeon, and killing
  a boss only advances the player who did it, not the whole world. Players
  sharing a room mutate the same live objects (verified with a real
  two-client run). Other players now show up on the 2D map in any room
  within your own fog-of-war, not just your current room, and combat/item
  events, arrivals, and departures broadcast to anyone who can see that
  room — not only someone standing in it. Persistence reshaped to match:
  the dungeon now lives in a per-world `world.json`, separate from each
  player's own smaller save, and survives server restarts. This ships the
  single-service version — multi-container routing (splitting a world
  across separately deployed containers) isn't part of it, noted below.
- **Narrated presence and a chat command.** Movement/arrival/departure
  broadcasts now carry actual text ("Aragorn enters the room."/"Aragorn
  leaves the room.") instead of just a silent map refresh. A new
  `say <message>` command lets players talk, deliberately scoped to a
  stricter same-room audience than combat/movement's fog-of-war rule —
  seeing a room on your map shouldn't mean overhearing it. Along the way,
  fixed a real defect chat exposed: every command used to be fully
  lowercased before dispatch, which would have silently mangled chat
  message casing; only the verb is lowercased now, and casing is preserved
  verbatim in what players say.

## Planned

### Persistent world across containers

The dungeon already persists across restarts of the one running service
(`world.json`, shipped above). What's not built: splitting a world's
dungeon across multiple separately-deployed containers, and the routing
layer the existing single-service world-select screen would then need in
front of it, to send a player's connection to whichever container their
chosen world actually lives on.

## Other ideas raised alongside these

Not yet committed to, but worth keeping in mind as the above lands:

- A leaderboard or hall of fame for completed runs.
- 2D graphics polish: motion/animation, real autotiling, and per-item icons
  (Phase 5 and the deferred pieces of Phases 3-4 in `2D-GRAPHICS-PLAN.md`),
  now that the first increment has shipped above.
