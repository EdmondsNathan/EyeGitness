from __future__ import annotations

from state import app_state
from views.tab_bar import LIST_FUNCS
from ansi.codes import INVERT, RESET


def refresh_files() -> None:
    list_func = LIST_FUNCS.get(app_state.current_tab)
    if list_func:
        app_state.refresh_file_list(list_func())


def render_simple_content() -> str:
    """Single-pane file list for unmodified tab."""
    refresh_files()
    files = app_state.file_cache
    if not files:
        return " (no files)\n"
    return "\n".join(files) + "\n"


def render_file_list() -> str:
    """Checkbox file list for interactive tabs."""
    refresh_files()
    files = app_state.file_cache
    if not files:
        return " (no files)\n"

    lines = []
    for i, f in enumerate(files):
        checked = "x" if f in app_state.checked_files else " "
        cursor = ""
        end = ""
        if i == app_state.cursor_index:
            cursor = INVERT
            end = RESET
        lines.append(f"{cursor}[{checked}] {f}{end}")
    return "\n".join(lines) + "\n"
