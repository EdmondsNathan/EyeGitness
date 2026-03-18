from __future__ import annotations

from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.containers import ConditionalContainer, Float
from prompt_toolkit.filters import Condition
from prompt_toolkit.widgets import Frame, TextArea

from eyegitness.state import app_state
from eyegitness.git.stat import commit


commit_text_area = TextArea(
    multiline=True,
    height=10,
    width=60,
)

commit_keybinds = KeyBindings()
commit_text_area.control.key_bindings = commit_keybinds


@commit_keybinds.add("escape")
def _cancel(event):
    commit_text_area.text = ""
    app_state.show_commit_dialog = False
    event.app.invalidate()
    # Focus moves automatically when the ConditionalContainer hides


@commit_keybinds.add("escape", "enter")
def _submit(event):
    message = commit_text_area.text.strip()
    if message:
        commit(message)
    commit_text_area.text = ""
    app_state.show_commit_dialog = False
    app_state.reset_for_tab()
    event.app.invalidate()
    # Focus moves automatically when the ConditionalContainer hides


commit_dialog = ConditionalContainer(
    content=Frame(
        commit_text_area,
        title="Commit Message  (Alt+Enter submit | Esc cancel)",
    ),
    filter=Condition(lambda: app_state.show_commit_dialog),
)

commit_float = Float(content=commit_dialog)
