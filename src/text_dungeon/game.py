from __future__ import annotations

from . import history
from .balance import MAX_DUNGEON_LEVEL
from .character import DEFAULT_PLAYER_CLASS, create_player
from .combat import resolve_attack
from .commands import handle_command as dispatch_command
from .leveling import XP_PER_LEVEL, gain_xp, xp_for_kill
from .minimap import compute_coords
from .minimap import render_map as build_map_lines
from .models import Item, Player, Room
from .templates import BOSS, MAX_ITEM_TIER, SKILL_TEMPLATES, SUPER_BOSS, WIN_ITEM_NAME
from .world import generate_dungeon, is_final_dungeon, room_count_range


class Game:
    def __init__(
        self,
        seed: int | None = None,
        *,
        player: Player | None = None,
        rooms: dict[str, Room] | None = None,
        running: bool = True,
        player_class: str | None = None,
        player_name: str | None = None,
    ) -> None:
        """Start a fresh dungeon, or, if `player`/`rooms` are given, resume a saved one."""
        self.player = player or create_player(player_class or DEFAULT_PLAYER_CLASS, name=player_name)
        if rooms is not None:
            self.rooms = rooms
            self.coords = compute_coords(self.rooms)
        else:
            self._enter_new_dungeon(seed)
        self.running = running
        self.output: list[str] = []

    def _enter_new_dungeon(self, seed: int | None) -> None:
        min_rooms, max_rooms = room_count_range(self.player.dungeon_level)
        final_boss = is_final_dungeon(self.player.dungeon_level)
        upgrade_slot = self.player.next_upgrade_slot
        equipped = getattr(self.player, upgrade_slot)
        upgrade_tier = min((equipped.tier if equipped else 0) + 1, MAX_ITEM_TIER)
        self.rooms = generate_dungeon(
            seed=seed,
            min_rooms=min_rooms,
            max_rooms=max_rooms,
            final_boss=final_boss,
            player_class=self.player.player_class,
            upgrade_slot=upgrade_slot,
            upgrade_tier=upgrade_tier,
        )
        self.coords = compute_coords(self.rooms)
        self.player.next_upgrade_slot = "off_hand" if upgrade_slot == "main_hand" else "main_hand"
        history.start_new_dungeon(self.player)

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
        s = self.status()
        print(
            f"[HP {s['hp']}/{s['max_hp']}  Lv {s['level']} (XP {s['xp']}/{s['xp_per_level']})  "
            f"Dungeon {s['dungeon_level']}/{s['max_dungeon_level']}]"
        )

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
            names = ", ".join(self._item_label(item) for item in room.items)
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
        self.look()

    def take(self, item_name: str) -> None:
        room = self.current_room()
        for item in room.items:
            if item.name == item_name:
                if item.player_class is not None and item.player_class != self.player.player_class:
                    self.emit(f"Only a {item.player_class} can wield the {item.name}.")
                    return
                room.items.remove(item)
                self.player.inventory.append(item)
                self.emit(f"You take the {self._item_label(item)}.")
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
        self.emit(f"Main hand: {self._equipped_line(self.player.main_hand)}")
        self.emit(f"Off hand: {self._equipped_line(self.player.off_hand)}")
        if not self.player.inventory:
            self.emit("You aren't carrying anything else.")
            return
        for item in self.player.inventory:
            self.emit(f"- {self._item_label(item)}: {item.description}")

    def _equipped_line(self, item: Item | None) -> str:
        return f"{self._item_label(item)}: {item.description}" if item else "(empty)"

    def _item_label(self, item: Item) -> str:
        """An item's name plus its mechanical effect, e.g. 'rusty sword (+2 damage)'."""
        effect = item.effect_summary()
        return f"{item.name} ({effect})" if effect else item.name

    def equip(self, item_name: str) -> None:
        if self.player.main_hand and self.player.main_hand.name == item_name:
            self.emit(f"You already have the {item_name} equipped.")
            return
        if self.player.off_hand and self.player.off_hand.name == item_name:
            self.emit(f"You already have the {item_name} equipped.")
            return

        for item in self.player.inventory:
            if item.name == item_name:
                if item.slot is None:
                    self.emit(f"You can't equip the {item.name}.")
                    return
                previous = getattr(self.player, item.slot)
                if previous is not None:
                    self.player.inventory.append(previous)
                self.player.inventory.remove(item)
                setattr(self.player, item.slot, item)
                self.emit(f"You equip the {self._item_label(item)}.")
                return
        self.emit(f"You don't have a '{item_name}'.")

    def unequip(self, item_name: str) -> None:
        for slot in ("main_hand", "off_hand"):
            item = getattr(self.player, slot)
            if item is not None and item.name == item_name:
                setattr(self.player, slot, None)
                self.player.inventory.append(item)
                self.emit(f"You unequip the {self._item_label(item)}.")
                return
        self.emit(f"You don't have '{item_name}' equipped.")

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

    def _skill_template(self, skill_name: str):
        return next((s for s in SKILL_TEMPLATES if s.name == skill_name), None)

    def show_skills(self) -> None:
        if not self.player.skills:
            self.emit("You don't know any skills yet.")
            return
        for skill_name in self.player.skills:
            skill = self._skill_template(skill_name)
            self.emit(
                f"- {skill.name} ({skill.mana_cost} mana): {skill.description} "
                f"Effect: {skill.effect_summary()}."
            )

    def cast(self, skill_name: str) -> None:
        if skill_name not in self.player.skills:
            self.emit(f"You don't know a skill called '{skill_name}'.")
            return

        skill = self._skill_template(skill_name)
        if skill_name in self.player.used_skills_this_round:
            self.emit(f"You've already used {skill.name} this round.")
            return
        if self.player.mana < skill.mana_cost:
            self.emit(
                f"You don't have enough mana to cast {skill.name} ({skill.mana_cost} needed)."
            )
            return

        self.player.mana -= skill.mana_cost
        self.player.used_skills_this_round.add(skill_name)
        for effect in skill.effects:
            self.emit(effect.apply(self.player, skill.name))

    def _map_lines(self) -> list[str]:
        return build_map_lines(
            self.rooms, self.coords, self.player.visited, self.player.current_room
        )

    def render_map(self) -> None:
        for line in self._map_lines():
            self.emit(line)

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
                "main_hand": self._item_summary(self.player.main_hand),
                "off_hand": self._item_summary(self.player.off_hand),
            },
            "inventory": [
                {
                    "name": item.name,
                    "description": item.description,
                    "effect": item.effect_summary(),
                }
                for item in self.player.inventory
            ],
            "skills": [
                {
                    "name": skill.name,
                    "description": skill.description,
                    "mana_cost": skill.mana_cost,
                    "effect": skill.effect_summary(),
                }
                for skill in (self._skill_template(name) for name in self.player.skills)
            ],
            "map_lines": self._map_lines(),
        }

    def _item_summary(self, item: Item | None) -> dict | None:
        if not item:
            return None
        return {
            "name": item.name,
            "description": item.description,
            "effect": item.effect_summary(),
        }

    def win(self) -> None:
        self.emit(
            f"You have conquered all {MAX_DUNGEON_LEVEL} dungeons and slain the "
            f"{SUPER_BOSS.monster_name}. Victory!"
        )
        self.running = False
