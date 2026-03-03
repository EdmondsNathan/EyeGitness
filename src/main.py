from prompt_toolkit import Application

from keybinds import global_keybinds
from views.layout import build_layout


def main():
    app = Application(
        layout=build_layout(),
        key_bindings=global_keybinds.global_keybinds,
        full_screen=True,
        refresh_interval=0.5,
    )
    app.run()


if __name__ == "__main__":
    main()
