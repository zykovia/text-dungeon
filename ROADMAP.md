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
  landing in one implicit world. Each world is an independently persisted
  save namespace (`<world_id>/<player_id>.json`); worlds the player already
  has a character in show that character's class, level, HP, dungeon floor,
  and item count right on the select screen, so they can recognize their own
  character before rejoining it. This is the player-facing half of the
  original design, built inside the one existing service: dungeons stay
  solo-per-player (no shared/concurrent state between players in a world
  yet) and there are no new containers. The multi-container routing part of
  the original design is still future work, noted below.

## Planned

### Multiplayer: shared dungeon

Let multiple players explore and fight in the same dungeon at the same time,
rather than each player generating their own independent instance.

### Persistent world per container

Persist the dungeon itself (not just per-player progress) on the running
container, so the world survives restarts and is shared by everyone
connected to it. Once dungeons are actually split across separate
containers, the existing single-service world-select screen also needs a
routing layer in front of it, to send a player's connection to whichever
container their chosen world actually lives on, rather than listing worlds
that all happen to live in the one service as it does today.

## Design note: multiplayer is one change, not two

"Multiplayer" and "persistent world" are really the same architectural
pivot. Today, `Game` owns exactly one player and one dungeon, generated and
saved per player. Sharing a dungeon across players means:

- The dungeon (rooms, monster HP, items) becomes a *world* object independent
  of any single player, persisted under its own id instead of a player's.
- Every connected player needs to see the effects of everyone else's actions
  in real time (someone else kills the monster in your room, takes the
  item), which means a broadcast layer per world, not just per-connection
  request/response like today.
- Concurrent mutation of shared state (two players attacking the same
  monster) needs to be made safe.
- Player identity, position, inventory, and XP stay per-player, but "respawn"
  and "advance to the next dungeon" become world-level events that need a
  policy: does the whole world advance when anyone kills the boss, or do
  respawns only relocate that one player?

This deserves its own design pass before implementation starts, separate
from the classes/items work, which was additive and self-contained by
comparison.

## Other ideas raised alongside these

Not yet committed to, but worth keeping in mind as the above lands:

- Player presence/chat once multiplayer exists (e.g. "Aragorn entered the
  room").
- A leaderboard or hall of fame for completed runs.
- 2D graphics with stock assets, replacing the text-based web client with a
  tile map. Phased approach written up in `2D-GRAPHICS-PLAN.md`.
