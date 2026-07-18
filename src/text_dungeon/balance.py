"""Tunable game-balance numbers, collected in one place for easy tweaking.

Names and flavor text for bosses/monsters/items/rooms live in templates/
instead; this file is just the numbers.
"""

# Dungeon sizing: each dungeon level adds this many rooms (min and max) over the last.
BASE_MIN_ROOMS = 6
BASE_MAX_ROOMS = 10
ROOMS_GROWTH_PER_DUNGEON_LEVEL = 2
MAX_DUNGEON_LEVEL = 7

# Room population: chance a non-boss room gets a monster / an item.
MONSTER_SPAWN_CHANCE = 0.5
ITEM_SPAWN_CHANCE = 0.6

# Boss stats.
BOSS_HP_RANGE = (22, 30)
BOSS_ATTACK_RANGE = (4, 6)
SUPER_BOSS_HP_RANGE = (45, 60)
SUPER_BOSS_ATTACK_RANGE = (8, 12)

# Leveling.
MONSTER_XP = 2
BOSS_XP = 5
SUPER_BOSS_XP = 20
XP_PER_LEVEL = 10
LEVEL_UP_HP_BONUS = 5

# Combat: random roll added on top of the base attack / incoming damage.
ATTACK_DAMAGE_ROLL = (0, 3)
INCOMING_DAMAGE_ROLL = (-1, 2)
