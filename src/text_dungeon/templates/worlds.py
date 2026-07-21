from dataclasses import dataclass


@dataclass(frozen=True)
class WorldTemplate:
    # id must be a bare slug (no "/", no "..") since it's used directly as a
    # save-directory name.
    id: str
    name: str
    description: str


WORLD_TEMPLATES = [
    WorldTemplate(
        "verdant-depths",
        "Verdant Depths",
        "Ruins swallowed by an ancient forest, roots grown through every wall.",
    ),
    WorldTemplate(
        "sunken-crypt",
        "Sunken Crypt",
        "Flooded catacombs beneath a drowned cathedral.",
    ),
    WorldTemplate(
        "ashen-spire",
        "Ashen Spire",
        "A tower gutted by fire long ago, still smoldering in its lowest halls.",
    ),
]


def world_template_for(world_id: str) -> WorldTemplate | None:
    """The template for a known world by id, if any."""
    return next((world for world in WORLD_TEMPLATES if world.id == world_id), None)
