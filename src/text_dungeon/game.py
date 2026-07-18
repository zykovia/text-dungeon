from __future__ import annotations

import random

from .models import Player, Room
from .world import build_world, compute_coords

HELP_TEXT = """
Commands:
  go <direction>   move north/south/east/west (n/s/e/w)
  look             describe the current room
  take <item>      pick up an item
  inventory (i)    show what you're carrying
  attack           attack the monster in the room
  use <item>       use an item from your inventory
  map (m)          show a map of rooms you've explored
  help             show this message
  quit             give up and leave the dungeon
""".strip()

DIRECTIONS = {"n": "north", "s": "south", "e": "east", "w": "west"}


class Game:
    def __init__(self) -> None:
        self.rooms = build_world()
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
        verb, _, arg = command.partition(" ")
        arg = arg.strip()

        if verb in DIRECTIONS:
            verb, arg = "go", DIRECTIONS[verb]

        handler = self.COMMANDS.get(verb)
        if handler is None:
            self.emit("You're not sure how to do that. Type 'help' for commands.")
            return
        handler(self, arg)

    def _cmd_go(self, arg: str) -> None:
        if not arg:
            self.emit("Go where?")
            return
        self.move(DIRECTIONS.get(arg, arg))

    def _cmd_look(self, arg: str) -> None:
        self.look()

    def _cmd_take(self, arg: str) -> None:
        if not arg:
            self.emit("Take what?")
            return
        self.take(arg)

    def _cmd_inventory(self, arg: str) -> None:
        self.show_inventory()

    def _cmd_attack(self, arg: str) -> None:
        self.attack()

    def _cmd_use(self, arg: str) -> None:
        if not arg:
            self.emit("Use what?")
            return
        self.use(arg)

    def _cmd_help(self, arg: str) -> None:
        for line in HELP_TEXT.splitlines():
            self.emit(line)

    def _cmd_quit(self, arg: str) -> None:
        self.emit("You flee the dungeon.")
        self.running = False

    def _cmd_map(self, arg: str) -> None:
        self.render_map()

    COMMANDS = {
        "go": _cmd_go,
        "look": _cmd_look,
        "take": _cmd_take,
        "inventory": _cmd_inventory,
        "i": _cmd_inventory,
        "inv": _cmd_inventory,
        "attack": _cmd_attack,
        "use": _cmd_use,
        "help": _cmd_help,
        "quit": _cmd_quit,
        "map": _cmd_map,
        "m": _cmd_map,
    }

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

        bonus = sum(item.damage_bonus for item in self.player.inventory)
        damage = self.player.attack + bonus + random.randint(0, 3)
        monster.hp -= damage
        self.emit(f"You strike the {monster.name} for {damage} damage.")

        if not monster.alive:
            self.emit(f"You have defeated the {monster.name}!")
            return

        incoming = max(0, monster.attack + random.randint(-1, 2))
        self.player.hp -= incoming
        self.emit(f"The {monster.name} hits you for {incoming} damage. ({self.player.hp}/{self.player.max_hp} HP)")

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
        visited = self.player.visited
        if not visited:
            self.emit("You haven't explored anywhere yet.")
            return

        known = set(visited)
        for room_id in visited:
            known.update(self.rooms[room_id].exits.values())

        xs = [self.coords[room_id][0] for room_id in known]
        ys = [self.coords[room_id][1] for room_id in known]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        room_at = {self.coords[room_id]: room_id for room_id in known}

        self.emit("")
        self.emit("Map:")
        for y in range(max_y, min_y - 1, -1):
            row = []
            for x in range(min_x, max_x + 1):
                room_id = room_at.get((x, y))
                if room_id is None:
                    row.append("   ")
                elif room_id == self.player.current_room:
                    row.append("[@]")
                elif room_id in visited:
                    row.append("[#]")
                else:
                    row.append("[?]")
            self.emit("".join(row))

    def win(self) -> None:
        self.emit("")
        self.emit("You place the golden crown upon your head. The dungeon trembles and falls silent.")
        self.emit("You have conquered Text Dungeon. Victory!")
        self.running = False
