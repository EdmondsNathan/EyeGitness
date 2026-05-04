"""Commit message dialog — a floating overlay for composing commits.

Opens when the user presses 's' on the Staged tab. Provides a multiline
text area with its own keybindings (Esc to cancel, Alt+Enter to submit).
The dialog floats over the main layout via prompt_toolkit's Float container.
"""

from __future__ import annotations

from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.containers import ConditionalContainer, Float
from prompt_toolkit.filters import Condition
from prompt_toolkit.widgets import Frame, TextArea

from eyegitness.state import app_state
from eyegitness.git.stat import commit

# Multiline text area for typing the commit message
commit_text_area = TextArea(
    multiline=True,
    height=10,
    width=60,
)

# Dedicated keybindings for the commit dialog (separate from global bindings)
commit_keybinds = KeyBindings()
commit_text_area.control.key_bindings = commit_keybinds


@commit_keybinds.add("escape")
def _cancel(event):
    """Close the commit dialog without committing, discarding the message."""
    commit_text_area.text = ""
    app_state.show_commit_dialog = False
    event.app.invalidate()
    # Focus moves automatically when the ConditionalContainer hides


@commit_keybinds.add("escape", "enter")
def _submit(event):
    """Submit the commit message (Alt+Enter). Empty messages are ignored."""
    message = commit_text_area.text.strip()
    if message:
        commit(message)
    commit_text_area.text = ""
    app_state.show_commit_dialog = False
    app_state.reset_for_tab()
    event.app.invalidate()
    # Focus moves automatically when the ConditionalContainer hides


# ConditionalContainer: only rendered when show_commit_dialog is True
commit_dialog = ConditionalContainer(
    content=Frame(
        commit_text_area,
        title="Commit Message  (Alt+Enter submit | Esc cancel)",
    ),
    filter=Condition(lambda: app_state.show_commit_dialog),
)

# Float wraps the dialog so it overlays the main layout
commit_float = Float(content=commit_dialog)
