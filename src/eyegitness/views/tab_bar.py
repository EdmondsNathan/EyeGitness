"""Tab bar rendering and tab configuration.

Defines the mapping between Tab enum values, their display labels, their
number-key shortcuts, and the git function that lists files for each tab.
Renders the tab bar as a single ANSI-styled line with file counts.
"""

from __future__ import annotations

from collections.abc import Callable

from eyegitness.state import Tab, app_state
from eyegitness.git.stat import list_modified, list_staged, list_untracked, list_unmodified
from eyegitness.ansi.codes import INVERT, RESET

# Master config: (Tab enum, display label, file-listing function)
# Order here determines display order in the tab bar
TAB_CONFIG: list[tuple[Tab, str, Callable[[], list[str]]]] = [
    (Tab.UNTRACKED, "[1] Untracked", list_untracked),
    (Tab.UNMODIFIED, "[2] Unmodified", list_unmodified),
    (Tab.MODIFIED, "[3] Modified", list_modified),
    (Tab.STAGED, "[4] Staged", list_staged),
    (Tab.LOG, "[5] Log", lambda: []),  # Log tab has no file list
]

# Lookup: number key -> Tab enum (for keybinding registration)
TAB_BY_NUMBER: dict[int, Tab] = {i: tab for i, (tab, _, _) in enumerate(TAB_CONFIG, 1)}

# Lookup: Tab enum -> file listing function (for file list rendering)
LIST_FUNC_BY_TAB: dict[Tab, Callable[[], list[str]]] = {
    tab: func for tab, _, func in TAB_CONFIG
}


def render_tab_bar() -> str:
    """Render the tab bar as an ANSI-styled string.

    Each tab shows its label and file count (except Log). The active tab
    is highlighted with inverted colors.
    """
    parts: list[str] = []
    for tab, label, list_func in TAB_CONFIG:
        if tab is Tab.LOG:
            text = f" {label} "
        else:
            # Show file count next to each tab label
            count = len(list_func())
            text = f" {label} ({count}) "
        # Invert colors for the active tab
        if tab == app_state.current_tab:
            parts.append(f"{INVERT}{text}{RESET}")
        else:
            parts.append(text)
    return " ".join(parts)
