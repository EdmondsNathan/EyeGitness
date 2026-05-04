"""Diff pane rendering for the right side of the split layout.

Fetches the appropriate diff (modified, staged, or untracked) based on the
current tab, applies syntax coloring, and handles both vertical and horizontal
scrolling. Scroll offsets are clamped to prevent overscroll.
"""

from __future__ import annotations

from eyegitness.state import Tab, app_state
from eyegitness.git.diff import diff_modified, diff_staged, diff_untracked
from eyegitness.ansi.colorizer import diff_colorize, ansi_hslice, ansi_visible_len

# Maps each tab to its diff-fetching function
DIFF_FUNCS = {
    Tab.UNTRACKED: diff_untracked,
    Tab.MODIFIED: diff_modified,
    Tab.STAGED: diff_staged,
}


def render_diff() -> str:
    """Render the colorized diff for the current tab with scroll support.

    For untracked files: shows checked files, or all files if none checked.
    For modified/staged: shows checked files, or the full diff if none checked.
    """
    diff_func = DIFF_FUNCS.get(app_state.current_tab)
    if diff_func is None:
        return ""

    # Determine which files to diff
    checked = sorted(app_state.checked_files)
    if app_state.current_tab == Tab.UNTRACKED:
        # Untracked tab: fall back to all cached files if nothing checked
        raw = diff_func(checked or app_state.file_cache)
    else:
        # Modified/Staged: pass None to get the full diff if nothing checked
        raw = diff_func(checked or None)

    # Colorize the diff output
    lines = diff_colorize(raw).splitlines()
    if not lines:
        return " (empty)\n"

    # Clamp vertical scroll offset
    max_vscroll = max(0, len(lines) - 1)
    app_state.diff_scroll_offset = min(app_state.diff_scroll_offset, max_vscroll)

    # Clamp horizontal scroll offset to the widest visible line
    max_width = max(ansi_visible_len(line) for line in lines)
    max_hscroll = max(0, max_width - 1)
    app_state.diff_hscroll_offset = min(app_state.diff_hscroll_offset, max_hscroll)

    # Apply vertical scroll (slice from offset onward)
    visible = lines[app_state.diff_scroll_offset:]
    # Apply horizontal scroll (ANSI-aware character slicing)
    if app_state.diff_hscroll_offset > 0:
        visible = [ansi_hslice(line, app_state.diff_hscroll_offset) for line in visible]
    return "\n".join(visible) + "\n"
