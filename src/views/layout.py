from prompt_toolkit import ANSI
from prompt_toolkit.layout.containers import HSplit, VSplit, Window, DynamicContainer
from prompt_toolkit.layout.dimension import D
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.layout import Layout

import state
from git.diff import diff_modified, diff_staged
from git.stat import (
    list_modified, list_staged, list_untracked, list_unmodified,
)
from ansi.colorizer import diff_colorize, ansi_hslice
from ansi.codes import INVERT, RESET, GREEN

TAB_LABELS = ["[1] Untracked", "[2] Unmodified", "[3] Modified", "[4] Staged"]

_list_funcs = {
    1: list_untracked,
    2: list_unmodified,
    3: list_modified,
    4: list_staged,
}


def _is_simple_tab():
    return state.current_tab in (1, 2)


def _tab_bar() -> str:
    parts = []
    for i, label in enumerate(TAB_LABELS, start=1):
        if i == state.current_tab:
            parts.append(f"\x1b[7m {label} \x1b[0m")
        else:
            parts.append(f" {label} ")
    return "  ".join(parts)


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

    focus_left = state.focus == 'left'
    lines = []
    for i, f in enumerate(files):
        checked = "x" if f in state.checked_files else " "
        cursor = ""
        end = ""
        if focus_left and i == state.cursor_index:
            cursor = INVERT
            end = RESET
        lines.append(f"{cursor}[{checked}] {f}{end}")
    return "\n".join(lines) + "\n"


def _right_content() -> str:
    checked = sorted(state.checked_files)
    tab = state.current_tab
    if tab == 3:
        text = diff_colorize(diff_modified(checked or None))
    elif tab == 4:
        text = diff_colorize(diff_staged(checked or None))
    else:
        return ""

    lines = text.splitlines()
    offset = state.diff_scroll_offset
    visible = lines[offset:]
    if not visible:
        return " (empty)\n"
    hoffset = state.diff_hscroll_offset
    if hoffset > 0:
        visible = [ansi_hslice(line, hoffset) for line in visible]
    return "\n".join(visible) + "\n"


def _left_title() -> str:
    indicator = ">" if state.focus == 'left' else " "
    return f"{indicator} Files"


def _right_title() -> str:
    indicator = ">" if state.focus == 'right' else " "
    return f"{indicator} Diff"


def _build_simple_body():
    """Single pane for untracked/unmodified tabs."""
    return Window(content=FormattedTextControl(
        lambda: ANSI(_simple_content()), show_cursor=False
    ))


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


def build_layout() -> Layout:
    tab_bar = Window(
        content=FormattedTextControl(lambda: ANSI(_tab_bar()), show_cursor=False),
        height=1,
    )

    separator = Window(height=1, char='─')

    body = DynamicContainer(_dynamic_body)

    root_container = HSplit([
        tab_bar,
        separator,
        body,
    ])

    return Layout(root_container)
