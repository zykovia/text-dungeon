from __future__ import annotations

import random

from .models import Player, Room
from .world import build_world

HELP_TEXT = """
Commands:
  go <direction>   move north/south/east/west (n/s/e/w)
  look             describe the current room
  take <item>      pick up an item
  inventory (i)    show what you're carrying
  attack           attack the monster in the room
  use <item>       use an item from your inventory
  help             show this message
  quit             give up and leave the dungeon
""".strip()

DIRECTIONS = {"n": "north", "s": "south", "e": "east", "w": "west"}


class Game:
    def __init__(self) -> None:
        self.rooms = build_world()
        self.player = Player(name="Adventurer")
        self.running = True

    def run(self) -> None:
        print("You descend into the dungeon. Type 'help' for a list of commands.\n")
        self.look()
        while self.running and self.player.alive:
            try:
                command = input("\n> ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                print("\nYou flee the dungeon.")
                return
            if command:
                self.handle_command(command)

        if not self.player.alive:
            print("\nYou have died. Game over.")

    def handle_command(self, command: str) -> None:
        verb, _, arg = command.partition(" ")
        arg = arg.strip()

        if verb in DIRECTIONS:
            verb, arg = "go", DIRECTIONS[verb]

        handler = self.COMMANDS.get(verb)
        if handler is None:
            print("You're not sure how to do that. Type 'help' for commands.")
            return
        handler(self, arg)

    def _cmd_go(self, arg: str) -> None:
        if not arg:
            print("Go where?")
            return
        self.move(DIRECTIONS.get(arg, arg))

    def _cmd_look(self, arg: str) -> None:
        self.look()

    def _cmd_take(self, arg: str) -> None:
        if not arg:
            print("Take what?")
            return
        self.take(arg)

    def _cmd_inventory(self, arg: str) -> None:
        self.show_inventory()

    def _cmd_attack(self, arg: str) -> None:
        self.attack()

    def _cmd_use(self, arg: str) -> None:
        if not arg:
            print("Use what?")
            return
        self.use(arg)

    def _cmd_help(self, arg: str) -> None:
        print(HELP_TEXT)

    def _cmd_quit(self, arg: str) -> None:
        print("You flee the dungeon.")
        self.running = False

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
    }

    def current_room(self) -> Room:
        return self.rooms[self.player.current_room]

    def look(self) -> None:
        room = self.current_room()
        print(f"\n== {room.name} ==")
        print(room.description)
        if room.monster and room.monster.alive:
            print(f"A {room.monster.name} blocks your path! ({room.monster.description})")
        if room.items:
            names = ", ".join(item.name for item in room.items)
            print(f"You see: {names}")
        print(f"Exits: {', '.join(sorted(room.exits))}")

    def move(self, direction: str) -> None:
        room = self.current_room()
        if room.monster and room.monster.alive:
            print(f"The {room.monster.name} blocks your way. You must attack or find another path.")
            return
        destination = room.exits.get(direction)
        if not destination:
            print("You can't go that way.")
            return
        self.player.current_room = destination
        self.look()

    def take(self, item_name: str) -> None:
        room = self.current_room()
        for item in room.items:
            if item.name == item_name:
                room.items.remove(item)
                self.player.inventory.append(item)
                print(f"You take the {item.name}.")
                if item.name == "golden crown":
                    self.win()
                return
        print(f"There's no '{item_name}' here.")

    def show_inventory(self) -> None:
        if not self.player.inventory:
            print("You aren't carrying anything.")
            return
        for item in self.player.inventory:
            print(f"- {item.name}: {item.description}")

    def attack(self) -> None:
        room = self.current_room()
        monster = room.monster
        if not monster or not monster.alive:
            print("There's nothing here to attack.")
            return

        bonus = sum(item.damage_bonus for item in self.player.inventory)
        damage = self.player.attack + bonus + random.randint(0, 3)
        monster.hp -= damage
        print(f"You strike the {monster.name} for {damage} damage.")

        if not monster.alive:
            print(f"You have defeated the {monster.name}!")
            return

        incoming = max(0, monster.attack + random.randint(-1, 2))
        self.player.hp -= incoming
        print(f"The {monster.name} hits you for {incoming} damage. ({self.player.hp}/{self.player.max_hp} HP)")

    def use(self, item_name: str) -> None:
        for item in self.player.inventory:
            if item.name == item_name:
                if item.heal:
                    healed = min(item.heal, self.player.max_hp - self.player.hp)
                    self.player.hp += healed
                    self.player.inventory.remove(item)
                    print(f"You use the {item.name} and recover {healed} HP. ({self.player.hp}/{self.player.max_hp} HP)")
                else:
                    print(f"You can't use the {item.name} right now.")
                return
        print(f"You don't have a '{item_name}'.")

    def win(self) -> None:
        print("\nYou place the golden crown upon your head. The dungeon trembles and falls silent.")
        print("You have conquered Text Dungeon. Victory!")
        self.running = False
