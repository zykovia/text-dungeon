from __future__ import annotations

from collections import deque

from .directions import DIRECTION_DELTAS
from .models import Room


def compute_coords(rooms: dict[str, Room], start: str = "entrance") -> dict[str, tuple[int, int]]:
    """Derive grid coordinates for each room by walking cardinal exits from `start`.

    Assumes the exit graph is a consistent planar grid (as built by generate_dungeon):
    a room reached two different ways would silently keep whichever coordinate it
    got first.
    """
    coords = {start: (0, 0)}
    queue = deque([start])
    while queue:
        room_id = queue.popleft()
        x, y = coords[room_id]
        for direction, dest in rooms[room_id].exits.items():
            delta = DIRECTION_DELTAS.get(direction)
            if delta is None or dest in coords:
                continue
            coords[dest] = (x + delta[0], y + delta[1])
            queue.append(dest)
    return coords


def known_room_ids(rooms: dict[str, Room], visited: set[str]) -> set[str]:
    """Every room the player has been in, plus its immediate unvisited neighbors.

    This is the one definition of "fog of war": what's revealed on the map
    beyond rooms actually stepped in.
    """
    known = set(visited)
    for room_id in visited:
        known.update(rooms[room_id].exits.values())
    return known


def room_snapshots(
    rooms: dict[str, Room],
    coords: dict[str, tuple[int, int]],
    visited: set[str],
    current_room: str,
) -> dict[str, dict]:
    """A UI-facing snapshot of every known room: position, and what's in it.

    Scoped to the same known set as render_map, so a 2D map and the ASCII
    map always agree on what's revealed.
    """
    snapshots = {}
    for room_id in known_room_ids(rooms, visited):
        room = rooms[room_id]
        x, y = coords[room_id]
        snapshots[room_id] = {
            "x": x,
            "y": y,
            "current": room_id == current_room,
            "visited": room_id in visited,
            "auto_advance": room.auto_advance,
            "monster": room.monster.name if room.monster and room.monster.alive else None,
            "items": [item.name for item in room.items],
        }
    return snapshots


def render_map(
    rooms: dict[str, Room],
    coords: dict[str, tuple[int, int]],
    visited: set[str],
    current_room: str,
) -> list[str]:
    """Render an ASCII minimap: '@' current room, '#' visited, '?' known-but-unvisited neighbor."""
    if not visited:
        return ["You haven't explored anywhere yet."]

    known = known_room_ids(rooms, visited)

    xs = [coords[room_id][0] for room_id in known]
    ys = [coords[room_id][1] for room_id in known]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    room_at = {coords[room_id]: room_id for room_id in known}

    lines = ["", "Map:"]
    for y in range(max_y, min_y - 1, -1):
        row = []
        for x in range(min_x, max_x + 1):
            room_id = room_at.get((x, y))
            if room_id is None:
                row.append("   ")
            elif room_id == current_room:
                row.append("[@]")
            elif room_id in visited:
                row.append("[#]")
            else:
                row.append("[?]")
        lines.append("".join(row))
    return lines
