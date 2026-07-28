# Story content draft (Phase 0)

Pure writing for `STORY-AND-WORLD-PLAN.md` Phase 0, no code. One entry per
world in `templates/worlds.py`. Tone matches the existing terse,
one-sentence-per-line style already used in `templates/rooms.py` and
`templates/monsters.py`. Nothing here is wired up yet: Phase 1 turns the
NPC pieces into a real mechanics module, Phase 2 scopes room/boss selection
per world and narrates the intro/victory beats at the existing world-entry
and final-boss-win hookpoints in `game.py`.

Each world keeps the current shared regular-boss/final-boss *mechanics*
(same HP/attack ranges from `balance.py`, same win item name `"golden
crown"`) — only the room dressing, monster name/description, and narration
around them differ per world. `vault_room` (the between-boss shop) is left
as-is; it's a mechanical room, not a story beat, so it's out of scope here.

---

## Verdant Depths

*Ruins swallowed by an ancient forest, roots grown through every wall.*

**World intro** (narrated on entering this world):
> The forest did not spare this place. Roots have pried the stonework
> apart stone by stone, and canopy light falls green and broken through
> cracks that used to be a roof. Somewhere below, something old still
> claims the ruin as its own.

**Room flavor** (replaces the generic pool for this world):
- Root-Choked Stair — Thick roots have grown through the steps, forcing you to climb over rather than up.
- Sunlit Breach — A collapsed section of ceiling lets pale green light spill across the moss.
- Vine-Strangled Hall — Vines have pulled two pillars down across the passage; you climb through the gap.
- Flooded Roots — Rainwater pools in a hollow of tangled roots, black with rot.
- Overgrown Barracks — Bunks have rotted to soil; saplings grow where soldiers once slept.

**Boss encounter** (regular boss, reused across this world's non-final dungeons):
- monster name: The Root-Bound Lord
- room name: Throne of Bark and Bone
- room description: Roots have grown into a crude throne, and something sits upon it, waiting.
- monster description: Bark has grown over its armor, but the blade in its hand is still iron.

**Victory beat** (final boss + crown, this world's win):
- monster name: The Verdant Sovereign
- room name: The Heart of the Depths
- room description: Every root in the ruin converges here, woven into a throne no stone was ever meant to hold.
- monster description: Old beyond counting, and still growing.
- crown description: A crown of interwoven roots and gold, warm to the touch.
- on-win narration: The roots loosen and fall still as the Sovereign collapses. For the first time in longer than the ruin has stood, the depths are quiet.

---

## Sunken Crypt

*Flooded catacombs beneath a drowned cathedral.*

**World intro:**
> The cathedral above drowned first; the crypt beneath it drowned with
> it. Black water has stood here so long the dead have learned to float.
> Whatever answers for this place waits below the flood line, and it
> isn't drowned at all.

**Room flavor:**
- Flooded Nave — Water has swallowed the pews; only the tips of stone angels break the surface.
- Drowned Reliquary — Shattered reliquaries litter a floor gone soft with rot and silt.
- Bell Chamber — A cracked bell lies half-submerged, tolling faintly whenever the water shifts.
- Weeping Wall — Water seeps constantly from a crack veined across the stone.
- Choir Loft — Waterlogged hymnals disintegrate at a touch; the loft still smells of incense.

**Boss encounter:**
- monster name: The Chancel Lord
- room name: The Drowned Chancel
- room description: Black water stands knee-deep before an altar that never stopped being used.
- monster description: It has not needed to breathe in a very long time.

**Victory beat:**
- monster name: The Cathedral Drowned
- room name: The Flooded Sanctum
- room description: The water here is deeper, older, and darker than anywhere else in the crypt.
- monster description: What the cathedral became after it stopped being a cathedral at all.
- crown description: A crown of tarnished silver, still dripping long after you lift it clear of the water.
- on-win narration: The water stills the moment it falls. For the first time since the flood, the crypt is silent all the way to the surface.

---

## Ashen Spire

*A tower gutted by fire long ago, still smoldering in its lowest halls.*

**World intro:**
> The fire that gutted this tower burned out on every floor but the
> lowest ones, which still smolder centuries later. Ash falls like snow
> indoors. Whatever kept that fire alive this long is still down there,
> feeding it.

**Room flavor:**
- Ember-Lit Landing — Embers glow faintly in the walls, throwing just enough light to see by.
- Charred Archive — Shelves of burnt books crumble to ash at the lightest touch.
- Collapsed Stairwell — Fire-weakened stone gave way here; you pick your way across the gap.
- Smoke-Choked Cell — Thin smoke still curls from a crack in the floor, centuries after the fire that made it.
- Ash-Drift Hall — Ash has drifted knee-deep against one wall, undisturbed for longer than you'd like to guess.

**Boss encounter:**
- monster name: The Cinder Lord
- room name: The Cinder Throne
- room description: Heat rolls off a throne built from fused, blackened stone.
- monster description: Its armor never cooled enough to stop glowing.

**Victory beat:**
- monster name: The Undying Ember
- room name: The Spire's Furnace Heart
- room description: This is the fire that never went out, and the thing that has kept it burning.
- monster description: Centuries of fire compressed into something that used to be a person.
- crown description: A crown of blackened gold, still warm from the furnace it was pulled out of.
- on-win narration: The furnace heart goes dark as it falls, and for the first time in longer than anyone alive remembers, the Ashen Spire is cold.

---

## Not covered here (deliberately, per Phase 0 scope)

- NPC dialogue lines — that's Phase 1's `templates/npcs.py`, once the
  `dialogue.py` mechanics module and `talk` command exist to say them
  through.
- The Phase 3 stretch quest flag and its flavor text — depends on Phase 1
  NPCs existing first.
