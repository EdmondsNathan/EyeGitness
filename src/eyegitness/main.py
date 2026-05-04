"""eyegitness — a terminal UI for visualizing git diffs and file status.

Entry point for the application. Creates and runs the prompt_toolkit Application
with a full-screen TUI layout, vim-style keybindings, and a 0.5s auto-refresh
interval to keep the display in sync with the working tree.
"""

from prompt_toolkit import Application

from eyegitness.keybinds.global_keybinds import global_keybinds
from eyegitness.views.layout import build_layout


def main() -> None:
    """Launch the eyegitness TUI."""
    app = Application(
        layout=build_layout(),        # Root layout: tab bar, body pane(s), status bar
        key_bindings=global_keybinds,  # Vim-style bindings (disabled when commit dialog is open)
        full_screen=True,              # Alternate screen buffer — no shell scrollback pollution
        refresh_interval=0.5,          # Re-render every 500ms to pick up external git changes
    )
    app.run()


if __name__ == "__main__":
    main()
