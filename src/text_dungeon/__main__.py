from .character import default_name_for_class
from .game import Game
from .templates import CLASS_TEMPLATES


def _prompt_for_class() -> str:
    print("Choose your class:")
    for i, template in enumerate(CLASS_TEMPLATES, start=1):
        print(f"  {i}) {template.name} - {template.description}")
    while True:
        choice = input("> ").strip()
        for i, template in enumerate(CLASS_TEMPLATES, start=1):
            if choice == str(i) or choice.lower() == template.name.lower():
                return template.name
        print("Not a valid choice, try again.")


def _prompt_for_name(player_class: str) -> str:
    default_name = default_name_for_class(player_class)
    print(f"Name your adventurer (press Enter for {default_name}):")
    name = input("> ").strip()
    return name or default_name


def main() -> None:
    player_class = _prompt_for_class()
    player_name = _prompt_for_name(player_class)
    Game(player_class=player_class, player_name=player_name).run()


if __name__ == "__main__":
    main()
