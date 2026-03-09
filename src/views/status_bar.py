from __future__ import annotations

import os

from state import app_state
from views.tab_bar import is_simple_tab
from git.stat import get_branch, get_head_short, get_ahead_behind
from ansi.colorizer import ansi_visible_len
from ansi.codes import INVERT, RESET, DIM, BOLD, YELLOW


def _pad_right(left: str, right: str) -> str:
    """Combine left and right text, padding so right is right-aligned."""
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
    if not is_simple_tab():
        left_parts.append(f"  {pos}/{total}")
        n_checked = len(app_state.checked_files)
        if n_checked > 0:
            left_parts.append(f"  {YELLOW}{n_checked} selected{RESET}")
    else:
        left_parts.append(f"  {total} files")

    left = "".join(left_parts)

    right_parts = []
    ahead, behind = get_ahead_behind()
    if ahead or behind:
        ab = []
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
    if is_simple_tab():
        left = " 1-4:tabs  q:quit"
        right = ""
    else:
        left = " j/k:navigate  Space:select  a:all  Enter:focus  q:quit"
        right_parts = []
        if app_state.diff_scroll_offset > 0:
            right_parts.append(f"Line {app_state.diff_scroll_offset}")
        right_parts.append("J/K:scroll  g/G:top/bottom  d/u:jump")
        right = "  ".join(right_parts)

    return f"{DIM}{INVERT}{_pad_right(left, f'{right} ')}{RESET}"
