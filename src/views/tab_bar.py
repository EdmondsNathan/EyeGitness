from __future__ import annotations

from collections.abc import Callable

from state import Tab, app_state
from git.stat import list_modified, list_staged, list_untracked, list_unmodified
from ansi.codes import INVERT, RESET

TAB_CONFIG: list[tuple[Tab, str, Callable[[], list[str]]]] = [
    (Tab.UNTRACKED, "[1] Untracked", list_untracked),
    (Tab.UNMODIFIED, "[2] Unmodified", list_unmodified),
    (Tab.MODIFIED, "[3] Modified", list_modified),
    (Tab.STAGED, "[4] Staged", list_staged),
    (Tab.LOG, "[5] Log", lambda: []),
]

TAB_BY_NUMBER: dict[int, Tab] = {i: tab for i, (tab, _, _) in enumerate(TAB_CONFIG, 1)}

LIST_FUNC_BY_TAB: dict[Tab, Callable[[], list[str]]] = {
    tab: func for tab, _, func in TAB_CONFIG
}


def render_tab_bar() -> str:
    parts: list[str] = []
    for tab, label, list_func in TAB_CONFIG:
        if tab is Tab.LOG:
            text = f" {label} "
        else:
            count = len(list_func())
            text = f" {label} ({count}) "
        if tab == app_state.current_tab:
            parts.append(f"{INVERT}{text}{RESET}")
        else:
            parts.append(text)
    return " ".join(parts)
