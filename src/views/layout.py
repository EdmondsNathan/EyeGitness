from prompt_toolkit import ANSI
from prompt_toolkit.layout.containers import HSplit, VSplit, Window
from prompt_toolkit.layout.dimension import D
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.layout import Layout

import state
from git.diff import diff_modified, diff_staged
from git.stat import stat_modified, stat_untracked, stat_unmodified, stat_staged
from ansi.colorizer import diff_colorize

TAB_LABELS = ["[1] Untracked", "[2] Unmodified", "[3] Modified", "[4] Staged"]


def _tab_bar() -> str:
    parts = []
    for i, label in enumerate(TAB_LABELS, start=1):
        if i == state.current_tab:
            parts.append(f"\x1b[7m {label} \x1b[0m")
        else:
            parts.append(f" {label} ")
    return "  ".join(parts)


def _left_content() -> str:
    tab = state.current_tab
    if tab == 1:
        files = stat_untracked()
        count = len(files.splitlines()) if files.strip() else 0
        return f"Untracked files: {count}\n"
    elif tab == 2:
        files = stat_unmodified()
        count = len(files.splitlines()) if files.strip() else 0
        return f"Unmodified files: {count}\n"
    elif tab == 3:
        return stat_modified()
    elif tab == 4:
        return stat_staged()
    return ""


def _right_content() -> str:
    tab = state.current_tab
    if tab == 1:
        return stat_untracked()
    elif tab == 2:
        return stat_unmodified()
    elif tab == 3:
        return diff_colorize(diff_modified())
    elif tab == 4:
        return diff_colorize(diff_staged())
    return ""


def build_layout() -> Layout:
    tab_bar = Window(
        content=FormattedTextControl(lambda: ANSI(_tab_bar()), show_cursor=False),
        height=1,
    )

    separator = Window(height=1, char='─')

    left_pane = HSplit([
        Window(content=FormattedTextControl(lambda: ANSI(_left_content()), show_cursor=False)),
    ], width=D(weight=1))

    right_pane = HSplit([
        Window(content=FormattedTextControl(lambda: ANSI(_right_content()), show_cursor=False)),
    ], width=D(weight=1))

    body = VSplit([
        left_pane,
        Window(width=1, char='│'),
        right_pane,
    ])

    root_container = HSplit([
        tab_bar,
        separator,
        body,
    ])

    return Layout(root_container)
