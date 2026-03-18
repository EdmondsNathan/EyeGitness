"""eyegitness — a terminal UI for visualizing git diffs and file status."""

from prompt_toolkit import Application

from eyegitness.keybinds.global_keybinds import global_keybinds
from eyegitness.views.layout import build_layout


def main() -> None:
    app = Application(
        layout=build_layout(),
        key_bindings=global_keybinds,
        full_screen=True,
        refresh_interval=0.5,
    )
    app.run()


if __name__ == "__main__":
    main()
