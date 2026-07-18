from dataclasses import dataclass


@dataclass(frozen=True)
class RoomTemplate:
    name: str
    description: str


ROOM_TEMPLATES = [
    RoomTemplate("Damp Hallway", "Water drips from the ceiling and pools on uneven stone."),
    RoomTemplate("Narrow Passage", "The walls press close enough to brush your shoulders."),
    RoomTemplate(
        "Collapsed Tunnel", "Rubble chokes half the passage; you squeeze through the rest."
    ),
    RoomTemplate("Old Armory", "Rusted weapon racks line the walls, mostly picked clean."),
    RoomTemplate(
        "Forgotten Crypt", "Stone sarcophagi line the walls. Something rattles in the dark."
    ),
    RoomTemplate("Sunken Chamber", "Ankle-deep water reflects your torchlight back at you."),
    RoomTemplate(
        "Guard Post", "An overturned table and scattered bones hint at a losing fight."
    ),
    RoomTemplate("Fungal Grotto", "Pale mushrooms cast a faint glow over slick stone."),
    RoomTemplate("Bone Pit", "A shallow pit crowded with bones, old and new."),
    RoomTemplate("Shrine Room", "A cracked altar stands before a faceless statue."),
]
