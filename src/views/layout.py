import os

from prompt_toolkit import ANSI
from prompt_toolkit.layout.containers import HSplit, VSplit, Window, DynamicContainer
from prompt_toolkit.layout.dimension import D
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.layout import Layout

import state
from git.diff import diff_modified, diff_staged, diff_untracked
from git.stat import (
    list_modified, list_staged, list_untracked, list_unmodified, get_branch,
)
from ansi.colorizer import diff_colorize, ansi_hslice, ansi_visible_len
from ansi.codes import INVERT, RESET, GREEN, DIM, BOLD, YELLOW

TAB_LABELS = ["[1] Untracked", "[2] Unmodified", "[3] Modified", "[4] Staged"]

_list_funcs = {
    1: list_untracked,
    2: list_unmodified,
    3: list_modified,
    4: list_staged,
}

_tab_list_funcs = [list_untracked, list_unmodified, list_modified, list_staged]


def _is_simple_tab():
    return state.current_tab in (2,)


def _tab_bar() -> str:
    parts = []
    for i, (label, list_func) in enumerate(zip(TAB_LABELS, _tab_list_funcs), start=1):
        count = len(list_func())
        text = f" {label} ({count}) "
        if i == state.current_tab:
            parts.append(f"\x1b[7m{text}\x1b[0m")
        else:
            parts.append(text)
    return " ".join(parts)


def _refresh_files():
    list_func = _list_funcs.get(state.current_tab)
    if list_func:
        state.refresh_file_list(list_func())


def _simple_content() -> str:
    """Single-pane file list for untracked/unmodified tabs."""
    _refresh_files()
    files = state.file_cache
    if not files:
        return " (no files)\n"
    return "\n".join(files) + "\n"


def _left_content() -> str:
    _refresh_files()
    files = state.file_cache
    if not files:
        return " (no files)\n"

    lines = []
    for i, f in enumerate(files):
        checked = "x" if f in state.checked_files else " "
        cursor = ""
        end = ""
        if i == state.cursor_index:
            cursor = INVERT
            end = RESET
        lines.append(f"{cursor}[{checked}] {f}{end}")
    return "\n".join(lines) + "\n"


def _right_content() -> str:
    checked = sorted(state.checked_files)
    tab = state.current_tab
    if tab == 1:
        text = diff_colorize(diff_untracked(checked or state.file_cache))
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
    state.diff_scroll_offset = min(state.diff_scroll_offset, max_vscroll)

    # Clamp horizontal scroll
    max_width = max(ansi_visible_len(line) for line in lines)
    max_hscroll = max(0, max_width - 1)
    state.diff_hscroll_offset = min(state.diff_hscroll_offset, max_hscroll)

    visible = lines[state.diff_scroll_offset:]
    hoffset = state.diff_hscroll_offset
    if hoffset > 0:
        visible = [ansi_hslice(line, hoffset) for line in visible]
    return "\n".join(visible) + "\n"


def _left_title() -> str:
    return " Files"


def _right_title() -> str:
    label = "Contents" if state.current_tab == 1 else "Diff"
    return f" {label}"


def _build_simple_body():
    """Single pane for unmodified tab."""
    title = Window(
        content=FormattedTextControl(
            lambda: ANSI(f"{GREEN}> Files{RESET}"), show_cursor=False
        ),
        height=1,
    )
    return HSplit([
        title,
        Window(content=FormattedTextControl(
            lambda: ANSI(_simple_content()), show_cursor=False
        )),
    ])


def _build_split_body():
    """Split pane with checkboxes + diff for modified/staged tabs."""
    left_title = Window(
        content=FormattedTextControl(
            lambda: ANSI(f"{GREEN}{_left_title()}{RESET}"), show_cursor=False
        ),
        height=1,
    )

    left_pane = HSplit([
        left_title,
        Window(content=FormattedTextControl(
            lambda: ANSI(_left_content()), show_cursor=False
        )),
    ], width=D(weight=1))

    right_title = Window(
        content=FormattedTextControl(
            lambda: ANSI(f"{GREEN}{_right_title()}{RESET}"), show_cursor=False
        ),
        height=1,
    )

    right_pane = HSplit([
        right_title,
        Window(content=FormattedTextControl(
            lambda: ANSI(_right_content()), show_cursor=False
        )),
    ], width=D(weight=1))

    return VSplit([
        left_pane,
        Window(width=1, char='│'),
        right_pane,
    ])


def _dynamic_body():
    if _is_simple_tab():
        return _build_simple_body()
    return _build_split_body()


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


def _status_row1() -> str:
    branch = get_branch() or "detached"
    total = len(state.file_cache)
    pos = state.cursor_index + 1 if total > 0 else 0

    left_parts = [f"{BOLD}[{branch}]{RESET}"]
    if not _is_simple_tab():
        left_parts.append(f"  {pos}/{total}")
        n_checked = len(state.checked_files)
        if n_checked > 0:
            left_parts.append(f"  {YELLOW}{n_checked} selected{RESET}")
    else:
        left_parts.append(f"  {total} files")

    left = "".join(left_parts)

    counts = []
    counts.append(f"M:{len(list_modified())}")
    counts.append(f"S:{len(list_staged())}")
    counts.append(f"U:{len(list_untracked())}")
    right = "  ".join(counts)

    return f"{DIM}{INVERT}{_pad_right(f' {left}', f'{right} ')}{RESET}"


def _status_row2() -> str:
    if _is_simple_tab():
        left = " 1-4:tabs  q:quit"
        right = ""
    else:
        left = " j/k:navigate  Space:select  a:all  Enter:jump  q:quit"
        right_parts = []
        if state.diff_scroll_offset > 0:
            right_parts.append(f"Line {state.diff_scroll_offset}")
        right_parts.append("H/L:scroll")
        right = "  ".join(right_parts)

    return f"{DIM}{INVERT}{_pad_right(left, f'{right} ')}{RESET}"


def build_layout() -> Layout:
    tab_bar = Window(
        content=FormattedTextControl(lambda: ANSI(_tab_bar()), show_cursor=False),
        height=1,
    )

    separator = Window(height=1, char='─')

    body = DynamicContainer(_dynamic_body)

    status_row1 = Window(
        content=FormattedTextControl(lambda: ANSI(_status_row1()), show_cursor=False),
        height=1,
    )
    status_row2 = Window(
        content=FormattedTextControl(lambda: ANSI(_status_row2()), show_cursor=False),
        height=1,
    )

    root_container = HSplit([
        tab_bar,
        separator,
        body,
        status_row1,
        status_row2,
    ])

    return Layout(root_container)
