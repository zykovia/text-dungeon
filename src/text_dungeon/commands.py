from __future__ import annotations

from typing import TYPE_CHECKING, Callable

from .directions import DIRECTION_SHORTHAND

if TYPE_CHECKING:
    from .game import Game

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


def _cmd_go(game: Game, arg: str) -> None:
    if not arg:
        game.emit("Go where?")
        return
    game.move(DIRECTION_SHORTHAND.get(arg, arg))


def _cmd_look(game: Game, arg: str) -> None:
    game.look()


def _cmd_take(game: Game, arg: str) -> None:
    if not arg:
        game.emit("Take what?")
        return
    game.take(arg)


def _cmd_inventory(game: Game, arg: str) -> None:
    game.show_inventory()


def _cmd_attack(game: Game, arg: str) -> None:
    game.attack()


def _cmd_use(game: Game, arg: str) -> None:
    if not arg:
        game.emit("Use what?")
        return
    game.use(arg)


def _cmd_help(game: Game, arg: str) -> None:
    for line in HELP_TEXT.splitlines():
        game.emit(line)


def _cmd_quit(game: Game, arg: str) -> None:
    game.emit("You flee the dungeon.")
    game.running = False


def _cmd_map(game: Game, arg: str) -> None:
    game.render_map()


COMMANDS: dict[str, Callable[[Game, str], None]] = {
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


def handle_command(game: Game, command: str) -> None:
    verb, _, arg = command.partition(" ")
    arg = arg.strip()

    if verb in DIRECTION_SHORTHAND:
        verb, arg = "go", DIRECTION_SHORTHAND[verb]

    handler = COMMANDS.get(verb)
    if handler is None:
        game.emit("You're not sure how to do that. Type 'help' for commands.")
        return
    handler(game, arg)
