from __future__ import annotations

from state import app_state
from git.diff import diff_modified, diff_staged, diff_untracked
from ansi.colorizer import diff_colorize, ansi_hslice, ansi_visible_len


def render_diff() -> str:
    checked = sorted(app_state.checked_files)
    tab = app_state.current_tab
    if tab == 1:
        text = diff_colorize(diff_untracked(checked or app_state.file_cache))
    elif tab == 3:
        text = diff_colorize(diff_modified(checked or None))
    elif tab == 4:
        text = diff_colorize(diff_staged(checked or None))
    else:
        return ""

    lines = text.splitlines()
    if not lines:
        return " (empty)\n"

    # Clamp vertical scroll
    max_vscroll = max(0, len(lines) - 1)
    app_state.diff_scroll_offset = min(app_state.diff_scroll_offset, max_vscroll)

    # Clamp horizontal scroll
    max_width = max(ansi_visible_len(line) for line in lines)
    max_hscroll = max(0, max_width - 1)
    app_state.diff_hscroll_offset = min(app_state.diff_hscroll_offset, max_hscroll)

    visible = lines[app_state.diff_scroll_offset:]
    hoffset = app_state.diff_hscroll_offset
    if hoffset > 0:
        visible = [ansi_hslice(line, hoffset) for line in visible]
    return "\n".join(visible) + "\n"
