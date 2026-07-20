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

## Planned

### Multiplayer: shared dungeon

Let multiple players explore and fight in the same dungeon at the same time,
rather than each player generating their own independent instance.

### Persistent world per container

Persist the dungeon itself (not just per-player progress) on the running
container, so the world survives restarts and is shared by everyone
connected to it.

### World select ingress

Once worlds are split across multiple containers, players need a way to pick
which one to join instead of being routed to a single fixed server. Planned
shape: a separate "world select" container/service that lists the available
world containers and acts as the entry point, routing the player's connection
to the world they choose. For a world the player already has a character in,
the list should show their status in that world (level/XP, HP, items held,
current floor) so they can recognize their own character and decide whether
to rejoin it, rather than just seeing an anonymous list of servers.

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

- Class-specific abilities beyond just starting gear (e.g. cleric heal,
  wizard spell).
- Player presence/chat once multiplayer exists (e.g. "Aragorn entered the
  room").
- A leaderboard or hall of fame for completed runs.
