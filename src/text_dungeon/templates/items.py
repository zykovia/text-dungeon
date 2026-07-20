from dataclasses import dataclass


@dataclass(frozen=True)
class ItemTemplate:
    name: str
    description: str
    heal: int = 0
    damage_bonus: int = 0
    player_class: str | None = None
    slot: str | None = None
    defense_bonus: int = 0
    tier: int = 1


MAX_ITEM_TIER = 7

# Each class's main-hand weapon across all 7 tiers (name, description, damage_bonus).
# Tier 1 is that class's starting weapon.
MAIN_HAND_LINES: dict[str, list[tuple[str, str, int]]] = {
    "Warrior": [
        ("rusty sword", "A worn blade, better than fists.", 2),
        ("iron sword", "Forged and balanced, a marked step up from rust and luck.", 4),
        ("steel sword", "Bright steel that holds an edge through a long fight.", 6),
        ("knight's blade", "Tempered for war, favored by seasoned soldiers.", 8),
        ("war cleaver", "A brutal, wide-bladed weapon built to end fights quickly.", 10),
        ("runed greatsword", "Etched with old battle-runes that hum when swung.", 12),
        ("dragonfang blade", "Said to be forged from a slain dragon's own fang.", 15),
    ],
    "Ranger": [
        ("dagger", "Quick and sharp, easy to conceal.", 1),
        ("honed dagger", "Freshly sharpened, it bites deeper than before.", 3),
        ("serrated dagger", "A jagged edge that tears as much as it cuts.", 5),
        ("assassin's blade", "Balanced for a killing strike from the shadows.", 7),
        ("shadowfang", "Blackened steel that seems to drink the torchlight.", 9),
        ("windcutter", "So light and quick it seems to cut the air itself.", 11),
        ("phantom edge", "A blade that leaves no mark until it's too late.", 14),
    ],
    "Cleric": [
        ("mace", "A heavy, blunt weapon blessed for battle.", 2),
        ("blessed mace", "Anointed in holy oil, it strikes true against evil.", 4),
        ("war mace", "A heavier head for a heavier judgment.", 6),
        ("mace of smiting", "Inscribed with a prayer for righteous force.", 8),
        ("sanctified maul", "Consecrated steel that burns the wicked.", 10),
        ("hammer of judgment", "Said to ring like a bell when it lands.", 12),
        ("mace of the divine", "A weapon carried by saints of old.", 15),
    ],
    "Wizard": [
        ("apprentice staff", "A gnarled length of wood humming with latent power.", 3),
        ("adept staff", "Carved with careful sigils that focus the will.", 5),
        ("journeyman staff", "A staff proven in real battle, not just study.", 7),
        ("arcane staff", "Crackles faintly with barely-contained energy.", 9),
        ("staff of embers", "Warm to the touch, it never fully cools.", 11),
        ("staff of the tempest", "Trails a faint static charge through the air.", 13),
        ("archmage's staff", "A staff whispered about in every school of magic.", 16),
    ],
}

# Each class's off-hand item across all 7 tiers (name, description, bonus, bonus_field).
# Warrior/Cleric lean on defense_bonus (a shield, a holy symbol); Ranger/Wizard lean on
# damage_bonus (a second blade, a spellbook), matching that class's tier-1 item.
OFF_HAND_LINES: dict[str, list[tuple[str, str, int, str]]] = {
    "Warrior": [
        ("wooden shield", "A sturdy round shield, scarred from old blows.", 2, "defense_bonus"),
        ("iron shield", "Heavier and harder to knock aside.", 4, "defense_bonus"),
        ("steel shield", "Polished steel that turns aside most blows.", 6, "defense_bonus"),
        ("tower shield", "Broad enough to cover from chin to knee.", 8, "defense_bonus"),
        ("knight's bulwark", "Bears a worn crest from some forgotten order.", 10, "defense_bonus"),
        ("runed aegis", "Old wardings glow faintly along its rim.", 12, "defense_bonus"),
        ("dragonscale wall", "Plated in scale said to shrug off dragonfire.", 15, "defense_bonus"),
    ],
    "Ranger": [
        ("hunting knife", "A second blade for a second strike.", 1, "damage_bonus"),
        ("throwing knife", "Weighted for a quick, thrown finish.", 2, "damage_bonus"),
        ("twin fang", "A matched blade, quick in an off-hand strike.", 3, "damage_bonus"),
        ("viper's tooth", "Thin, curved, and quicker than it looks.", 4, "damage_bonus"),
        ("silent thorn", "Makes no sound leaving its sheath.", 5, "damage_bonus"),
        ("nightsting", "A blade best drawn when no one's looking.", 6, "damage_bonus"),
        ("reaper's kiss", "The last thing a great many foes have felt.", 8, "damage_bonus"),
    ],
    "Cleric": [
        ("holy symbol", "A blessed emblem that turns aside harm.", 1, "defense_bonus"),
        ("silver symbol", "Cool silver that seems to steady the hand.", 2, "defense_bonus"),
        ("blessed icon", "Carried by clerics through a hundred campaigns.", 3, "defense_bonus"),
        ("sacred relic", "A fragment of something once much larger.", 4, "defense_bonus"),
        ("saint's medallion", "Said to have belonged to a saint who never fell.", 5, "defense_bonus"),
        ("radiant sigil", "Warm light seeps from its edges.", 6, "defense_bonus"),
        ("symbol of the divine", "Faith made solid, and nearly unbreakable.", 8, "defense_bonus"),
    ],
    "Wizard": [
        ("spellbook", "A well-worn tome of minor incantations.", 1, "damage_bonus"),
        ("tome of minor arcana", "Denser, trickier spells than the last book held.", 2, "damage_bonus"),
        ("tome of elements", "Chapters on fire, frost, and lightning alike.", 3, "damage_bonus"),
        ("grimoire of secrets", "Bound in something that isn't quite leather.", 4, "damage_bonus"),
        ("forbidden codex", "Its previous owner is conspicuously not around.", 5, "damage_bonus"),
        ("tome of the void", "The pages are colder than the room around them.", 6, "damage_bonus"),
        ("codex of the archmage", "The last book most wizards ever need.", 8, "damage_bonus"),
    ],
}


def _main_hand_templates() -> list[ItemTemplate]:
    return [
        ItemTemplate(
            name,
            description,
            damage_bonus=bonus,
            player_class=player_class,
            slot="main_hand",
            tier=tier,
        )
        for player_class, tiers in MAIN_HAND_LINES.items()
        for tier, (name, description, bonus) in enumerate(tiers, start=1)
    ]


def _off_hand_templates() -> list[ItemTemplate]:
    templates = []
    for player_class, tiers in OFF_HAND_LINES.items():
        for tier, (name, description, bonus, bonus_field) in enumerate(tiers, start=1):
            templates.append(
                ItemTemplate(
                    name,
                    description,
                    player_class=player_class,
                    slot="off_hand",
                    tier=tier,
                    **{bonus_field: bonus},
                )
            )
    return templates


POTION_TEMPLATES = [
    ItemTemplate("health potion", "A vial of red liquid that mends wounds.", heal=8),
    ItemTemplate("bandage", "Rough cloth, better than nothing.", heal=4),
]


ITEM_TEMPLATES = [
    *_main_hand_templates(),
    *_off_hand_templates(),
    *POTION_TEMPLATES,
]


def item_template_for(player_class: str, slot: str, tier: int) -> ItemTemplate | None:
    """The weapon/off-hand template for a class's given slot at a given tier, if any."""
    for template in ITEM_TEMPLATES:
        if (
            template.player_class == player_class
            and template.slot == slot
            and template.tier == tier
        ):
            return template
    return None
