from __future__ import annotations

from .models import Room
from .world import generate_dungeon, is_final_dungeon, room_count_range


class World:
    """Persistent, shared dungeon state for one world_id.

    Holds every dungeon level's rooms generated so far. A level is generated
    once, lazily, on first request, and never regenerated afterward, so
    multiple players can be on different levels of the same world without
    disturbing each other.

    level_rooms must stay fully synchronous (no `await`, directly or
    transitively): the single-process concurrency argument in
    MULTIPLAYER-DESIGN.md depends on generate-on-first-access completing as
    one uninterrupted step.
    """

    def __init__(self, levels: dict[int, dict[str, Room]] | None = None) -> None:
        self.levels: dict[int, dict[str, Room]] = levels if levels is not None else {}

    def level_rooms(
        self,
        level: int,
        *,
        player_class: str | None,
        upgrade_slot: str | None,
        upgrade_tier: int | None,
        seed: int | None = None,
    ) -> dict[str, Room]:
        """The rooms for `level`, generating and caching them on first request.

        player_class/upgrade_slot/upgrade_tier only bias generation the first
        time this level is created (whoever reaches it first); later visitors
        of a different class just see whatever's already there. A cheaper,
        deferred alternative (widening the loot pool to more than one class
        rather than a single bias) was considered but not built for this pass.
        """
        if level not in self.levels:
            min_rooms, max_rooms = room_count_range(level)
            self.levels[level] = generate_dungeon(
                seed=seed,
                min_rooms=min_rooms,
                max_rooms=max_rooms,
                final_boss=is_final_dungeon(level),
                player_class=player_class,
                upgrade_slot=upgrade_slot,
                upgrade_tier=upgrade_tier,
            )
        return self.levels[level]
