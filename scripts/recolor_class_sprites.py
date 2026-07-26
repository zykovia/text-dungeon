#!/usr/bin/env python3
"""Recolor 0x72 DungeonTileset II female player frames into themed class sprites.

One-off asset tool, not a runtime dependency (Pillow is not in pyproject.toml).
Install Pillow before running: python3 -m pip install pillow

Base frames (knight_f, elf_f, dwarf_f, wizzard_f idle_anim_f0, 16x28 CC0 art from
0x72's "16x16 DungeonTileset II") are not vendored in this repo; fetch them first,
e.g. from https://0x72.itch.io/dungeontileset-ii or the mirror at
https://github.com/marceloferreira357/bun-crawler-client/tree/main/public/sprites/0x72_DungeonTilesetII_v1.7/frames

Usage:
    python3 scripts/recolor_class_sprites.py <base_frames_dir> <output_dir>
"""

import sys
from pathlib import Path

from PIL import Image

# Each map is old RGBA -> new RGBA, built from the exact palette present in the
# source frame. Preserves the existing outline/shading ramp; only re-hues.
#
# The dwarf_f base was tried for Cleric and rejected: its beard silhouette reads
# as a bearded gnome regardless of color, since palette-swapping can't change
# silhouette. knight_f is reused for both Warrior and Cleric instead (a plain
# palette-swap of one rig for two units), which is the same trick the source
# pack's own "royal/heavy/elite knight" variants use.
COLOR_MAPS = [
    {
        "source": "knight_f_idle_anim_f0.png",
        "output": "warrior_f_idle_anim_f0.png",
        "map": {
            (114, 214, 206, 255): (196, 42, 42, 255),   # armor base: teal -> imperial red
            (65, 112, 137, 255): (120, 20, 20, 255),    # armor shadow -> dark red
            (253, 247, 237, 255): (250, 210, 110, 255), # trim highlight -> gold
            (220, 74, 123, 255): (35, 26, 22, 255),     # helmet plume -> near-black
            (247, 134, 151, 255): (72, 54, 44, 255),    # plume highlight -> dark brown
        },
        # Hand touch-up after this map, for a Chinese-female-warrior read: the
        # plume colors were pushed further toward true black hair ((35,26,22)
        # -> (20,18,20), (72,54,44) -> (42,38,46)), one pixel recolored to red
        # as a ribbon accent, and a few pixels of flowing hair added in the
        # empty margins beside the shoulders (same margins used for the
        # Cleric's wing accent below). Same rig/silhouette as knight_f
        # throughout, still shared with Cleric.
    },
    {
        "source": "elf_f_idle_anim_f0.png",
        "output": "ranger_f_idle_anim_f0.png",
        "map": {
            (250, 203, 62, 255): (184, 115, 51, 255),   # hair: gold -> bronze
            (252, 203, 163, 255): (196, 146, 104, 255), # skin -> tanned
            (75, 167, 71, 255): (107, 124, 49, 255),    # tunic -> olive green
            (238, 142, 46, 255): (150, 100, 53, 255),   # accent -> leather brown
            (61, 115, 79, 255): (63, 74, 32, 255),      # tunic shadow -> dark olive
            (218, 78, 56, 255): (176, 101, 45, 255),    # accent -> copper
            (86, 152, 204, 255): (214, 186, 140, 255),  # small accent -> bronze glint
        },
    },
    {
        "source": "knight_f_idle_anim_f0.png",
        "output": "cleric_f_idle_anim_f0.png",
        "map": {
            (114, 214, 206, 255): (235, 235, 240, 255), # armor base: teal -> white
            (65, 112, 137, 255): (196, 30, 40, 255),    # armor shadow/chest stripe -> red cross
            (253, 247, 237, 255): (245, 235, 210, 255), # trim highlight -> pale gold
            (220, 74, 123, 255): (214, 178, 60, 255),   # helmet plume -> gold
            (247, 134, 151, 255): (235, 205, 120, 255), # plume highlight -> light gold
        },
        # Hand touch-up after this map, for an angel/saint read: a floating
        # gold halo ring (2px) added in the blank rows above the helmet, plus
        # small white wing-tip accents in the empty margins beside the
        # shoulders. Same knight_f rig/silhouette throughout, still shared
        # with Warrior.
    },
    {
        "source": "wizzard_f_idle_anim_f0.png",
        "output": "wizard_f_idle_anim_f0.png",
        "map": {
            (86, 152, 204, 255): (106, 58, 130, 255),   # robe base: blue -> violet
            (89, 86, 189, 255): (45, 25, 60, 255),      # robe shadow -> near-black violet
            (181, 128, 87, 255): (32, 26, 28, 255),     # hair -> near-black
            (138, 80, 62, 255): (18, 14, 16, 255),      # hair shadow -> darker still
            (211, 191, 169, 255): (198, 188, 204, 255), # highlight -> cool grey-violet
            # (253, 247, 237, 255) skin/trim: left unchanged
        },
        # wizzard_f's face is a large "hair"-colored mass covering the lower
        # face (a beard silhouette carried over from the pack's wizard rig
        # regardless of gender). A palette swap can't fix a silhouette, so
        # after running this map, the beard-zone pixels (rows 17-20, roughly
        # columns 7-11) were manually repainted to skin, and the row16
        # remnant plus rows 19-20 shadow pixels cleaned up too, leaving the
        # row17/18 outline pixels as a pair of eyes. See git history for the
        # exact before/after diff on wizard_f_idle_anim_f0.png.
    },
]


def recolor(src: Path, dest: Path, color_map: dict) -> None:
    image = Image.open(src).convert("RGBA")
    pixels = image.load()
    for y in range(image.height):
        for x in range(image.width):
            pixel = pixels[x, y]
            if pixel in color_map:
                pixels[x, y] = color_map[pixel]
    image.save(dest)


def main() -> None:
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    base_dir, out_dir = Path(sys.argv[1]), Path(sys.argv[2])
    out_dir.mkdir(parents=True, exist_ok=True)
    for spec in COLOR_MAPS:
        src_path = base_dir / spec["source"]
        dest_path = out_dir / spec["output"]
        recolor(src_path, dest_path, spec["map"])
        print(f"{spec['source']} -> {dest_path.name}")


if __name__ == "__main__":
    main()
