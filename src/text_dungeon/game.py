from __future__ import annotations

from . import history, inventory, skills
from .balance import MAX_DUNGEON_LEVEL
from .character import DEFAULT_PLAYER_CLASS, create_player
from .combat import resolve_attack
from .commands import handle_command as dispatch_command
from .leveling import XP_PER_LEVEL, gain_xp, xp_for_kill
from .minimap import compute_coords, known_room_ids, room_snapshots
from .minimap import render_map as build_map_lines
from .models import Player, Room
from .templates import BOSS, MAX_ITEM_TIER, SUPER_BOSS, WIN_ITEM_NAME, skill_template_for
from .world import is_final_dungeon
from .world_state import World


class Game:
    def __init__(
        self,
        seed: int | None = None,
        *,
        player: Player | None = None,
        world: World | None = None,
        running: bool = True,
        player_class: str | None = None,
        player_name: str | None = None,
    ) -> None:
        """Start a fresh dungeon, or, if `player` is given, resume a saved one.

        `world` is the shared dungeon state to draw rooms from; left unset, a
        private, unshared World is created (solo play, and every existing
        test that doesn't care about multiplayer).
        """
        self.player = player or create_player(player_class or DEFAULT_PLAYER_CLASS, name=player_name)
        self.world = world if world is not None else World()
        self._load_current_level(seed)
        self.running = running
        self.output: list[str] = []
        self.last_broadcast: tuple[int, str, str] | None = None
        self.last_chat: str | None = None

    def _load_current_level(self, seed: int | None = None) -> None:
        """Point self.rooms/coords at the player's current level in the shared world.

        Side-effect-free on purpose: this runs on every construction,
        including a plain reconnect to an already-in-progress level, so it
        must not re-mark history or re-toggle upgrade bookkeeping (see
        advance(), which does those explicitly for a real level transition).
        """
        upgrade_slot = self.player.next_upgrade_slot
        equipped = getattr(self.player, upgrade_slot)
        upgrade_tier = min((equipped.tier if equipped else 0) + 1, MAX_ITEM_TIER)
        self.rooms = self.world.level_rooms(
            self.player.dungeon_level,
            player_class=self.player.player_class,
            upgrade_slot=upgrade_slot,
            upgrade_tier=upgrade_tier,
            seed=seed,
        )
        self.coords = compute_coords(self.rooms)
        if self.player.current_room not in self.rooms:
            # Self-heal a save whose room no longer exists in the loaded
            # world (e.g. the world state was lost/rolled back after this
            # room was already visited) instead of crashing on first look().
            self.player.current_room = "entrance"
            self.player.visited = set()

    def respawn(self) -> None:
        """Return to the entrance of the current (persistent) level after death."""
        self.player.current_room = "entrance"
        self.player.hp = self.player.max_hp
        self.emit("You awaken at the entrance, patched up and ready to continue.")
        self.look()

    def advance(self, seed: int | None = None) -> None:
        """Descend into the next level after defeating its boss."""
        self.player.dungeon_level += 1
        self.player.current_room = "entrance"
        self.player.hp = self.player.max_hp
        self.player.visited = set()
        self._load_current_level(seed)
        history.start_new_dungeon(self.player)
        self.player.next_upgrade_slot = (
            "off_hand" if self.player.next_upgrade_slot == "main_hand" else "main_hand"
        )
        self.emit(
            f"A new dungeon awaits below, larger than the last (depth {self.player.dungeon_level})."
        )
        self.look()

    def emit(self, text: str = "") -> None:
        self.output.append(text)
        history.record(self.player, text)

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
                command = input("\n> ").strip()
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
        s = self.status()
        print(
            f"[HP {s['hp']}/{s['max_hp']}  Lv {s['level']} (XP {s['xp']}/{s['xp_per_level']})  "
            f"Dungeon {s['dungeon_level']}/{s['max_dungeon_level']}]"
        )

    def handle_command(self, command: str) -> None:
        self.last_broadcast = None
        self.last_chat = None
        dispatch_command(self, command)

    def current_room(self) -> Room:
        return self.rooms[self.player.current_room]

    def knows_room(self, dungeon_level: int, room_id: str) -> bool:
        """Whether this player's own fog-of-war currently reveals this room.

        Used by the multiplayer broadcast layer to decide who to notify of
        an event elsewhere in the shared world. Checks dungeon_level first
        since room ids are only unique within a single level.
        """
        return self.player.dungeon_level == dungeon_level and room_id in known_room_ids(
            self.rooms, self.player.visited
        )

    def look(self) -> None:
        room = self.current_room()
        self.player.visited.add(room.id)
        self.emit("")
        self.emit(f"== {room.name} ==")
        self.emit(room.description)
        if room.monster and room.monster.alive:
            self.emit(f"A {room.monster.name} blocks your path! ({room.monster.description})")
        if room.items:
            names = ", ".join(inventory.item_label(item) for item in room.items)
            self.emit(f"You see: {names}")
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
        destination_room = self.rooms[destination]
        if destination_room.auto_advance:
            self.emit("")
            self.emit(f"== {destination_room.name} ==")
            self.emit(destination_room.description)
            self.advance()
            return
        self.look()

    def take(self, item_name: str) -> None:
        room = self.current_room()
        result = inventory.take_item(self.player, room, item_name)
        if result.item is None:
            self.emit(f"There's no '{item_name}' here.")
            return
        if result.blocked_by_class:
            self.emit(f"Only a {result.item.player_class} can wield the {result.item.name}.")
            return
        self.emit(f"You take the {inventory.item_label(result.item)}.")
        self.last_broadcast = (
            self.player.dungeon_level, room.id, f"{self.player.name} takes the {result.item.name}."
        )
        if result.item.name == WIN_ITEM_NAME:
            self.emit("")
            self.emit(
                "You place the golden crown upon your head. "
                "The dungeon trembles and falls silent."
            )
            if is_final_dungeon(self.player.dungeon_level):
                self.win()
            else:
                self.advance()

    def show_inventory(self) -> None:
        for line in inventory.inventory_lines(self.player):
            self.emit(line)

    def equip(self, item_name: str) -> None:
        if self.player.main_hand and self.player.main_hand.name == item_name:
            self.emit(f"You already have the {item_name} equipped.")
            return
        if self.player.off_hand and self.player.off_hand.name == item_name:
            self.emit(f"You already have the {item_name} equipped.")
            return

        item = next((i for i in self.player.inventory if i.name == item_name), None)
        if item is None:
            self.emit(f"You don't have a '{item_name}'.")
            return
        if item.slot is None:
            self.emit(f"You can't equip the {item.name}.")
            return
        inventory.equip_item(self.player, item)
        self.emit(f"You equip the {inventory.item_label(item)}.")

    def unequip(self, item_name: str) -> None:
        item = inventory.unequip_item(self.player, item_name)
        if item is None:
            self.emit(f"You don't have '{item_name}' equipped.")
            return
        self.emit(f"You unequip the {inventory.item_label(item)}.")

    def current_dungeon_history(self) -> list[str]:
        return history.current_dungeon_history(self.player)

    def show_history(self) -> None:
        """Print everything the player has done this playthrough, across all dungeons."""
        if not self.player.history:
            self.emit("Nothing has happened yet.")
            return
        for line in self.player.history:
            self.output.append(line)

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
            self.last_broadcast = (
                self.player.dungeon_level,
                room.id,
                f"{self.player.name} has defeated the {monster.name}!",
            )
            xp_gained = xp_for_kill(monster.name, BOSS.monster_name, SUPER_BOSS.monster_name)
            level_ups = gain_xp(self.player, xp_gained)
            self.emit(f"You gain {xp_gained} experience. ({self.player.xp} XP)")
            for level_up in level_ups:
                self.emit(
                    f"You reached level {level_up.level}! "
                    f"Max HP is now {level_up.max_hp}, and you feel fully healed."
                )
                if level_up.skill_learned:
                    self.emit(f"You've learned {level_up.skill_learned}!")
            if room.auto_advance:
                self.advance()
            return

        self.last_broadcast = (
            self.player.dungeon_level, room.id, f"{self.player.name} attacks the {monster.name}."
        )
        self.emit(
            f"The {monster.name} hits you for {result.incoming_damage} damage. "
            f"({self.player.hp}/{self.player.max_hp} HP)"
        )

    def use(self, item_name: str) -> None:
        result = inventory.use_item(self.player, item_name)
        if result.item is None:
            self.emit(f"You don't have a '{item_name}'.")
            return
        if not result.item.heal:
            self.emit(f"You can't use the {result.item.name} right now.")
            return
        self.emit(
            f"You use the {result.item.name} and recover {result.healed} HP. "
            f"({self.player.hp}/{self.player.max_hp} HP)"
        )

    def say(self, message: str) -> None:
        if not message:
            self.emit("Say what?")
            return
        if len(message) > 200:
            self.emit("That's too long to say. Try something shorter.")
            return
        self.emit(f"You say: {message}")
        self.last_chat = f"{self.player.name} says: {message}"

    def show_skills(self) -> None:
        if not self.player.skills:
            self.emit("You don't know any skills yet.")
            return
        for skill_name in self.player.skills:
            skill = skill_template_for(skill_name)
            self.emit(
                f"- {skill.name} ({skill.mana_cost} mana): {skill.description} "
                f"Effect: {skill.effect_summary()}."
            )

    def cast(self, skill_name: str) -> None:
        if skill_name not in self.player.skills:
            self.emit(f"You don't know a skill called '{skill_name}'.")
            return

        skill = skill_template_for(skill_name)
        if skill_name in self.player.used_skills_this_round:
            self.emit(f"You've already used {skill.name} this round.")
            return
        if self.player.mana < skill.mana_cost:
            self.emit(
                f"You don't have enough mana to cast {skill.name} ({skill.mana_cost} needed)."
            )
            return

        for message in skills.apply_skill(self.player, skill):
            self.emit(message)

    def _map_lines(self) -> list[str]:
        return build_map_lines(
            self.rooms, self.coords, self.player.visited, self.player.current_room
        )

    def render_map(self) -> None:
        for line in self._map_lines():
            self.emit(line)

    def _known_rooms(self) -> dict[str, dict]:
        return room_snapshots(
            self.rooms, self.coords, self.player.visited, self.player.current_room
        )

    def status(self) -> dict:
        """A snapshot of everything a UI needs for a stats/map/inventory sidebar."""
        return {
            "name": self.player.name,
            "hp": self.player.hp,
            "max_hp": self.player.max_hp,
            "mana": self.player.mana,
            "max_mana": self.player.max_mana,
            "player_class": self.player.player_class,
            "level": self.player.level,
            "xp": self.player.xp,
            "xp_per_level": XP_PER_LEVEL,
            "dungeon_level": self.player.dungeon_level,
            "max_dungeon_level": MAX_DUNGEON_LEVEL,
            "equipment": {
                "main_hand": inventory.item_summary(self.player.main_hand),
                "off_hand": inventory.item_summary(self.player.off_hand),
            },
            "inventory": [
                inventory.item_summary(item)
                for item in self.player.inventory
                if not item.retired
            ],
            "old_gear": [item.name for item in self.player.inventory if item.retired],
            "skills": [
                {
                    "name": skill.name,
                    "description": skill.description,
                    "mana_cost": skill.mana_cost,
                    "effect": skill.effect_summary(),
                }
                for skill in (skill_template_for(name) for name in self.player.skills)
            ],
            "map_lines": self._map_lines(),
            "rooms": self._known_rooms(),
        }

    def win(self) -> None:
        self.emit(
            f"You have conquered all {MAX_DUNGEON_LEVEL} dungeons and slain the "
            f"{SUPER_BOSS.monster_name}. Victory!"
        )
        self.running = False
