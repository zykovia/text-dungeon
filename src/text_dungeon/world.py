from .models import Item, Monster, Room


def build_world() -> dict[str, Room]:
    return {
        "entrance": Room(
            id="entrance",
            name="Dungeon Entrance",
            description=(
                "A crumbling stone archway leads down into darkness. "
                "Torches flicker on the walls."
            ),
            exits={"north": "hallway"},
        ),
        "hallway": Room(
            id="hallway",
            name="Damp Hallway",
            description=(
                "Water drips from the ceiling. Passages lead north and east, "
                "and south back outside."
            ),
            exits={"north": "armory", "east": "crypt", "south": "entrance"},
        ),
        "armory": Room(
            id="armory",
            name="Old Armory",
            description="Rusted weapon racks line the walls, mostly picked clean.",
            exits={"south": "hallway"},
            items=[Item("rusty sword", "A worn blade, better than fists.", damage_bonus=2)],
        ),
        "crypt": Room(
            id="crypt",
            name="Forgotten Crypt",
            description="Stone sarcophagi line the walls. Something rattles in the dark.",
            exits={"west": "hallway", "north": "boss_chamber"},
            items=[Item("health potion", "A vial of red liquid that mends wounds.", heal=8)],
            monster=Monster(
                "skeleton", hp=10, attack=2, description="A rattling pile of animated bones."
            ),
        ),
        "boss_chamber": Room(
            id="boss_chamber",
            name="Throne of the Dungeon Lord",
            description="A massive figure sits upon a throne of bones, waiting.",
            exits={"south": "crypt"},
            items=[Item("golden crown", "The Dungeon Lord's crown. Proof of your victory.")],
            monster=Monster(
                "Dungeon Lord",
                hp=25,
                attack=5,
                description="The master of this dungeon, clad in black iron.",
            ),
        ),
    }
