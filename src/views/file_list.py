from __future__ import annotations

from state import app_state
from views.tab_bar import LIST_FUNC_BY_TAB
from ansi.codes import INVERT, RESET


def refresh_files() -> None:
    list_func = LIST_FUNC_BY_TAB.get(app_state.current_tab)
    if list_func:
        app_state.refresh_file_list(list_func())


def render_simple_content() -> str:
    """Single-pane file list for the unmodified tab."""
    refresh_files()
    if not app_state.file_cache:
        return " (no files)\n"
    return "\n".join(app_state.file_cache) + "\n"


def render_file_list() -> str:
    """Checkbox file list for tabs with a diff view."""
    refresh_files()
    if not app_state.file_cache:
        return " (no files)\n"

    lines: list[str] = []
    for i, filename in enumerate(app_state.file_cache):
        checked = "x" if filename in app_state.checked_files else " "
        if i == app_state.cursor_index:
            lines.append(f"{INVERT}[{checked}] {filename}{RESET}")
        else:
            lines.append(f"[{checked}] {filename}")
    return "\n".join(lines) + "\n"
