"""File list rendering for the left pane.

Provides two rendering modes:
- ``render_simple_content``: Plain scrollable file list (for the Unmodified tab)
- ``render_file_list``: Checkbox file list with cursor highlighting (for diff tabs)

Both call ``refresh_files()`` each render cycle to keep the list in sync with git.
"""

from __future__ import annotations

from eyegitness.state import app_state
from eyegitness.views.tab_bar import LIST_FUNC_BY_TAB
from eyegitness.ansi.codes import INVERT, RESET


def refresh_files() -> None:
    """Re-fetch the file list for the current tab and update app state.

    Called at the start of each render cycle. Uses the tab-specific git
    function to get the latest file list and prune stale selections.
    """
    list_func = LIST_FUNC_BY_TAB.get(app_state.current_tab)
    if list_func:
        app_state.refresh_file_list(list_func())


def render_simple_content() -> str:
    """Single-pane file list for the unmodified tab with vertical scrolling.

    Shows plain filenames with no checkboxes or cursor. Supports vertical
    scrolling via J/K keys (reuses diff_scroll_offset for scroll position).
    """
    refresh_files()
    if not app_state.file_cache:
        return " (no files)\n"

    lines = app_state.file_cache
    # Clamp scroll offset to valid range
    max_vscroll = max(0, len(lines) - 1)
    app_state.diff_scroll_offset = min(app_state.diff_scroll_offset, max_vscroll)

    # Slice from scroll offset onward (prompt_toolkit clips to window height)
    visible = lines[app_state.diff_scroll_offset:]
    return "\n".join(visible) + "\n"


def render_file_list() -> str:
    """Checkbox file list for tabs with a diff view.

    Each file is shown as ``[x] filename`` (checked) or ``[ ] filename``.
    The cursor row is highlighted with inverted colors.
    """
    refresh_files()
    if not app_state.file_cache:
        return " (no files)\n"

    lines: list[str] = []
    for i, filename in enumerate(app_state.file_cache):
        checked = "x" if filename in app_state.checked_files else " "
        if i == app_state.cursor_index:
            # Highlight the cursor row with inverted colors
            lines.append(f"{INVERT}[{checked}] {filename}{RESET}")
        else:
            lines.append(f"[{checked}] {filename}")
    return "\n".join(lines) + "\n"
