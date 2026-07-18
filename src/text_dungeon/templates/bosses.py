from dataclasses import dataclass


@dataclass(frozen=True)
class BossTemplate:
    monster_name: str
    room_name: str
    room_description: str
    monster_description: str
    crown_description: str


BOSS = BossTemplate(
    monster_name="Dungeon Lord",
    room_name="Throne of the Dungeon Lord",
    room_description="A massive figure sits upon a throne of bones, waiting.",
    monster_description="The master of this dungeon, clad in black iron.",
    crown_description="The Dungeon Lord's crown. Proof of your victory.",
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
)

WIN_ITEM_NAME = "golden crown"
