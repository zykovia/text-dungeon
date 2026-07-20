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

## Planned

### Character classes

Add selectable classes: Warrior, Ranger, Cleric, Wizard. Each gets its own
starting stats and starting gear.

### Class-specific items

Items found in the dungeon become class-restricted where it makes sense
(weapons, class gear), while generic items (health potions, etc.) stay
usable by everyone.

### Multiplayer: shared dungeon

Let multiple players explore and fight in the same dungeon at the same time,
rather than each player generating their own independent instance.

### Persistent world per container

Persist the dungeon itself (not just per-player progress) on the running
container, so the world survives restarts and is shared by everyone
connected to it.

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
from the classes/items work, which is additive and self-contained by
comparison.

## Other ideas raised alongside these

Not yet committed to, but worth keeping in mind as the above lands:

- Equipment slots (weapon/armor) instead of a flat inventory list.
- Class-specific abilities beyond just starting gear (e.g. cleric heal,
  wizard spell).
- Player presence/chat once multiplayer exists (e.g. "Aragorn entered the
  room").
- A leaderboard or hall of fame for completed runs.
