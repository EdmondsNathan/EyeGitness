from __future__ import annotations

from state import Tab, app_state
from git.diff import diff_modified, diff_staged, diff_untracked
from ansi.colorizer import diff_colorize, ansi_hslice, ansi_visible_len

DIFF_FUNCS = {
    Tab.UNTRACKED: diff_untracked,
    Tab.MODIFIED: diff_modified,
    Tab.STAGED: diff_staged,
}


def render_diff() -> str:
    diff_func = DIFF_FUNCS.get(app_state.current_tab)
    if diff_func is None:
        return ""

    checked = sorted(app_state.checked_files)
    if app_state.current_tab == Tab.UNTRACKED:
        raw = diff_func(checked or app_state.file_cache)
    else:
        raw = diff_func(checked or None)

    lines = diff_colorize(raw).splitlines()
    if not lines:
        return " (empty)\n"

    max_vscroll = max(0, len(lines) - 1)
    app_state.diff_scroll_offset = min(app_state.diff_scroll_offset, max_vscroll)

    max_width = max(ansi_visible_len(line) for line in lines)
    max_hscroll = max(0, max_width - 1)
    app_state.diff_hscroll_offset = min(app_state.diff_hscroll_offset, max_hscroll)

    visible = lines[app_state.diff_scroll_offset:]
    if app_state.diff_hscroll_offset > 0:
        visible = [ansi_hslice(line, app_state.diff_hscroll_offset) for line in visible]
    return "\n".join(visible) + "\n"
