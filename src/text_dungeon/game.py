from __future__ import annotations

from .balance import MAX_DUNGEON_LEVEL
from .combat import resolve_attack
from .commands import handle_command as dispatch_command
from .leveling import XP_PER_LEVEL, gain_xp, xp_for_kill
from .minimap import compute_coords
from .minimap import render_map as build_map_lines
from .models import Player, Room
from .templates import BOSS, SUPER_BOSS, WIN_ITEM_NAME
from .world import generate_dungeon, is_final_dungeon, room_count_range


class Game:
    def __init__(self, seed: int | None = None) -> None:
        self.player = Player(name="Adventurer")
        self._enter_new_dungeon(seed)
        self.running = True
        self.output: list[str] = []

    def _enter_new_dungeon(self, seed: int | None) -> None:
        min_rooms, max_rooms = room_count_range(self.player.dungeon_level)
        final_boss = is_final_dungeon(self.player.dungeon_level)
        self.rooms = generate_dungeon(
            seed=seed, min_rooms=min_rooms, max_rooms=max_rooms, final_boss=final_boss
        )
        self.coords = compute_coords(self.rooms)

    def _relocate_to_entrance(self) -> None:
        self.player.current_room = "entrance"
        self.player.hp = self.player.max_hp
        self.player.visited = set()

    def respawn(self, seed: int | None = None) -> None:
        """Start a new dungeon of the same size after death, keeping inventory, level, and XP."""
        self._enter_new_dungeon(seed)
        self._relocate_to_entrance()
        self.emit("You awaken at the entrance of a new dungeon, your gear and experience intact.")
        self.look()

    def advance(self, seed: int | None = None) -> None:
        """Descend into a new, larger dungeon after defeating the boss."""
        self.player.dungeon_level += 1
        self._enter_new_dungeon(seed)
        self._relocate_to_entrance()
        self.emit(
            f"A new dungeon awaits below, larger than the last (depth {self.player.dungeon_level})."
        )
        self.look()

    def emit(self, text: str = "") -> None:
        self.output.append(text)

    def pop_output(self) -> list[str]:
        lines, self.output = self.output, []
        return lines

    def intro(self) -> None:
        self.emit("You descend into the dungeon. Type 'help' for a list of commands.")
        self.look()

    def run(self) -> None:
        self.intro()
        self._flush()
        while self.running:
            try:
                command = input("\n> ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                print("\nYou flee the dungeon.")
                return
            if command:
                self.handle_command(command)
                if not self.player.alive:
                    self.emit("")
                    self.emit("You have died.")
                    self.respawn()
                self._flush()

    def _flush(self) -> None:
        for line in self.pop_output():
            print(line)

    def handle_command(self, command: str) -> None:
        dispatch_command(self, command)

    def current_room(self) -> Room:
        return self.rooms[self.player.current_room]

    def look(self) -> None:
        room = self.current_room()
        self.player.visited.add(room.id)
        self.emit("")
        self.emit(f"== {room.name} ==")
        self.emit(room.description)
        if room.monster and room.monster.alive:
            self.emit(f"A {room.monster.name} blocks your path! ({room.monster.description})")
        if room.items:
            names = ", ".join(item.name for item in room.items)
            self.emit(f"You see: {names}")
        self.emit(
            f"HP: {self.player.hp}/{self.player.max_hp}  "
            f"Level: {self.player.level}  XP: {self.player.xp}/{XP_PER_LEVEL}"
        )
        self.emit(f"Exits: {', '.join(sorted(room.exits))}")

    def move(self, direction: str) -> None:
        room = self.current_room()
        if room.monster and room.monster.alive:
            self.emit(
                f"The {room.monster.name} blocks your way. You must attack or find another path."
            )
            return
        destination = room.exits.get(direction)
        if not destination:
            self.emit("You can't go that way.")
            return
        self.player.current_room = destination
        self.look()

    def take(self, item_name: str) -> None:
        room = self.current_room()
        for item in room.items:
            if item.name == item_name:
                room.items.remove(item)
                self.player.inventory.append(item)
                self.emit(f"You take the {item.name}.")
                if item.name == WIN_ITEM_NAME:
                    self.emit("")
                    self.emit(
                        "You place the golden crown upon your head. "
                        "The dungeon trembles and falls silent."
                    )
                    if is_final_dungeon(self.player.dungeon_level):
                        self.win()
                    else:
                        self.advance()
                return
        self.emit(f"There's no '{item_name}' here.")

    def show_inventory(self) -> None:
        if not self.player.inventory:
            self.emit("You aren't carrying anything.")
            return
        for item in self.player.inventory:
            self.emit(f"- {item.name}: {item.description}")

    def attack(self) -> None:
        room = self.current_room()
        monster = room.monster
        if not monster or not monster.alive:
            self.emit("There's nothing here to attack.")
            return

        result = resolve_attack(self.player, monster)
        self.emit(f"You strike the {monster.name} for {result.damage_dealt} damage.")

        if result.monster_defeated:
            self.emit(f"You have defeated the {monster.name}!")
            xp_gained = xp_for_kill(monster.name, BOSS.monster_name, SUPER_BOSS.monster_name)
            level_ups = gain_xp(self.player, xp_gained)
            self.emit(f"You gain {xp_gained} experience. ({self.player.xp} XP)")
            for level_up in level_ups:
                self.emit(
                    f"You reached level {level_up.level}! "
                    f"Max HP is now {level_up.max_hp}, and you feel fully healed."
                )
            return

        self.emit(
            f"The {monster.name} hits you for {result.incoming_damage} damage. "
            f"({self.player.hp}/{self.player.max_hp} HP)"
        )

    def use(self, item_name: str) -> None:
        for item in self.player.inventory:
            if item.name == item_name:
                if item.heal:
                    healed = min(item.heal, self.player.max_hp - self.player.hp)
                    self.player.hp += healed
                    self.player.inventory.remove(item)
                    self.emit(
                        f"You use the {item.name} and recover {healed} HP. "
                        f"({self.player.hp}/{self.player.max_hp} HP)"
                    )
                else:
                    self.emit(f"You can't use the {item.name} right now.")
                return
        self.emit(f"You don't have a '{item_name}'.")

    def render_map(self) -> None:
        for line in build_map_lines(
            self.rooms, self.coords, self.player.visited, self.player.current_room
        ):
            self.emit(line)

    def win(self) -> None:
        self.emit(
            f"You have conquered all {MAX_DUNGEON_LEVEL} dungeons and slain the "
            f"{SUPER_BOSS.monster_name}. Victory!"
        )
        self.running = False
