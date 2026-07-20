from dataclasses import dataclass


@dataclass(frozen=True)
class BossTemplate:
    monster_name: str
    room_name: str
    room_description: str
    monster_description: str
    vault_room_name: str
    vault_room_description: str
    crown_description: str | None = None


BOSS = BossTemplate(
    monster_name="Dungeon Lord",
    room_name="Throne of the Dungeon Lord",
    room_description="A massive figure sits upon a throne of bones, waiting.",
    monster_description="The master of this dungeon, clad in black iron.",
    vault_room_name="Stairs Beyond the Throne",
    vault_room_description=(
        "Behind the throne, a stone stairway spirals down into darkness, "
        "deeper into the dungeon."
    ),
)

SUPER_BOSS = BossTemplate(
    monster_name="Dungeon Emperor",
    room_name="The Emperor's Sanctum",
    room_description=(
        "The air itself seems to bend around the towering figure on the obsidian throne."
    ),
    monster_description=(
        "The true master of every dungeon, radiating a power that dwarfs any lord before him."
    ),
    crown_description="The Dungeon Emperor's crown. Proof you have conquered every dungeon.",
    vault_room_name="The Emperor's Reliquary",
    vault_room_description=(
        "Beyond the sanctum, a hidden chamber holds the empire's most sacred relic."
    ),
)

WIN_ITEM_NAME = "golden crown"
