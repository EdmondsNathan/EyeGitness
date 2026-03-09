from __future__ import annotations

from state import app_state
from git.stat import list_modified, list_staged, list_untracked, list_unmodified

TAB_LABELS = ["[1] Untracked", "[2] Unmodified", "[3] Modified", "[4] Staged"]

TAB_LIST_FUNCS = [list_untracked, list_unmodified, list_modified, list_staged]

LIST_FUNCS = {
    1: list_untracked,
    2: list_unmodified,
    3: list_modified,
    4: list_staged,
}


def is_simple_tab() -> bool:
    return app_state.current_tab in (2,)


def render_tab_bar() -> str:
    parts = []
    for i, (label, list_func) in enumerate(zip(TAB_LABELS, TAB_LIST_FUNCS), start=1):
        count = len(list_func())
        text = f" {label} ({count}) "
        if i == app_state.current_tab:
            parts.append(f"\x1b[7m{text}\x1b[0m")
        else:
            parts.append(text)
    return " ".join(parts)
