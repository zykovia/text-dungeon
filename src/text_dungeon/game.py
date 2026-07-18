from __future__ import annotations

from .combat import resolve_attack
from .commands import handle_command as dispatch_command
from .leveling import XP_PER_LEVEL, gain_xp, xp_for_kill
from .minimap import compute_coords
from .minimap import render_map as build_map_lines
from .models import Player, Room
from .world import BOSS_NAME, generate_dungeon


class Game:
    def __init__(self, seed: int | None = None) -> None:
        self.rooms = generate_dungeon(seed=seed)
        self.coords = compute_coords(self.rooms)
        self.player = Player(name="Adventurer")
        self.running = True
        self.output: list[str] = []

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
        while self.running and self.player.alive:
            try:
                command = input("\n> ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                print("\nYou flee the dungeon.")
                return
            if command:
                self.handle_command(command)
                self._flush()

        if not self.player.alive:
            self.emit("")
            self.emit("You have died. Game over.")
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
            self.emit(f"The {room.monster.name} blocks your way. You must attack or find another path.")
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
                if item.name == "golden crown":
                    self.win()
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
            xp_gained = xp_for_kill(monster.name, BOSS_NAME)
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
                    self.emit(f"You use the {item.name} and recover {healed} HP. ({self.player.hp}/{self.player.max_hp} HP)")
                else:
                    self.emit(f"You can't use the {item.name} right now.")
                return
        self.emit(f"You don't have a '{item_name}'.")

    def render_map(self) -> None:
        for line in build_map_lines(self.rooms, self.coords, self.player.visited, self.player.current_room):
            self.emit(line)

    def win(self) -> None:
        self.emit("")
        self.emit("You place the golden crown upon your head. The dungeon trembles and falls silent.")
        self.emit("You have conquered Text Dungeon. Victory!")
        self.running = False
