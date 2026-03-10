from __future__ import annotations

import os

from state import Tab, app_state
from git.stat import get_branch, get_head_short, get_ahead_behind
from ansi.colorizer import ansi_visible_len
from ansi.codes import INVERT, RESET, DIM, BOLD, YELLOW


def _pad_right(left: str, right: str) -> str:
    """Combine left and right text, padding so right is flush to the terminal edge."""
    try:
        width = os.get_terminal_size().columns
    except OSError:
        width = 80
    left_len = ansi_visible_len(left)
    right_len = ansi_visible_len(right)
    gap = max(1, width - left_len - right_len)
    return left + " " * gap + right


def render_status_row1() -> str:
    branch = get_branch() or "detached"
    total = len(app_state.file_cache)
    pos = app_state.cursor_index + 1 if total > 0 else 0

    left_parts = [f"{BOLD}[{branch}]{RESET}"]
    if app_state.current_tab.has_diff_view:
        left_parts.append(f"  {pos}/{total}")
        n_checked = len(app_state.checked_files)
        if n_checked > 0:
            left_parts.append(f"  {YELLOW}{n_checked} selected{RESET}")
    else:
        left_parts.append(f"  {total} files")

    left = "".join(left_parts)

    right_parts: list[str] = []
    ahead, behind = get_ahead_behind()
    if ahead or behind:
        ab: list[str] = []
        if ahead:
            ab.append(f"+{ahead}")
        if behind:
            ab.append(f"-{behind}")
        right_parts.append("".join(ab))
    head = get_head_short()
    if head:
        right_parts.append(head)
    right = "  ".join(right_parts)

    return f"{DIM}{INVERT}{_pad_right(f' {left}', f'{right} ')}{RESET}"


def render_status_row2() -> str:
    if not app_state.current_tab.has_diff_view:
        left = " 1-4:tabs  q:quit"
        right = ""
    else:
        if app_state.current_tab is Tab.STAGED:
            stage_hints = "s:commit  S:unstage"
        elif app_state.current_tab is Tab.MODIFIED:
            stage_hints = "s:stage"
        elif app_state.current_tab is Tab.UNTRACKED:
            stage_hints = "s:track"
        else:
            stage_hints = ""
        stage_part = f"  {stage_hints}" if stage_hints else ""
        left = f" j/k:navigate  Space:select  a:all  Enter:focus{stage_part}  q:quit"
        right_parts: list[str] = []
        if app_state.diff_scroll_offset > 0:
            right_parts.append(f"Line {app_state.diff_scroll_offset}")
        right_parts.append("J/K:scroll  g/G:top/bottom  d/u:jump")
        right = "  ".join(right_parts)

    return f"{DIM}{INVERT}{_pad_right(left, f'{right} ')}{RESET}"
