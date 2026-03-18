from __future__ import annotations

from prompt_toolkit import ANSI
from prompt_toolkit.layout.containers import FloatContainer, HSplit, VSplit, Window, DynamicContainer
from prompt_toolkit.layout.dimension import D
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.layout import Layout

from eyegitness.state import Tab, app_state
from eyegitness.views.tab_bar import render_tab_bar
from eyegitness.views.file_list import render_simple_content, render_file_list
from eyegitness.views.diff_view import render_diff
from eyegitness.views.log_view import render_log
from eyegitness.views.status_bar import render_status_row1, render_status_row2
from eyegitness.ansi.codes import RESET, GREEN
from eyegitness.views.commit_dialog import commit_float


def _right_pane_title() -> str:
    label = "Contents" if app_state.current_tab == Tab.UNTRACKED else "Diff"
    return f" {label}"


def _build_simple_body() -> HSplit:
    """Single pane for the unmodified tab."""
    title = Window(
        content=FormattedTextControl(
            lambda: ANSI(f"{GREEN}> Files{RESET}"), show_cursor=False
        ),
        height=1,
    )
    return HSplit([
        title,
        Window(content=FormattedTextControl(
            lambda: ANSI(render_simple_content()), show_cursor=False
        )),
    ])


def _build_split_body() -> VSplit:
    """Two-pane layout: file list on the left, diff on the right."""
    left_title = Window(
        content=FormattedTextControl(
            lambda: ANSI(f"{GREEN} Files{RESET}"), show_cursor=False
        ),
        height=1,
    )
    left_pane = HSplit([
        left_title,
        Window(content=FormattedTextControl(
            lambda: ANSI(render_file_list()), show_cursor=False
        )),
    ], width=D(weight=1))

    right_title = Window(
        content=FormattedTextControl(
            lambda: ANSI(f"{GREEN}{_right_pane_title()}{RESET}"), show_cursor=False
        ),
        height=1,
    )
    right_pane = HSplit([
        right_title,
        Window(content=FormattedTextControl(
            lambda: ANSI(render_diff()), show_cursor=False
        )),
    ], width=D(weight=1))

    return VSplit([
        left_pane,
        Window(width=1, char='|'),
        right_pane,
    ])


def _build_log_body() -> HSplit:
    """Single pane for the log tab."""
    title = Window(
        content=FormattedTextControl(
            lambda: ANSI(f"{GREEN} Commit Log{RESET}"), show_cursor=False
        ),
        height=1,
    )
    return HSplit([
        title,
        Window(content=FormattedTextControl(
            lambda: ANSI(render_log()), show_cursor=False
        )),
    ])


def _dynamic_body() -> HSplit | VSplit:
    if app_state.current_tab is Tab.LOG:
        return _build_log_body()
    if app_state.current_tab.has_diff_view:
        return _build_split_body()
    return _build_simple_body()


def build_layout() -> Layout:
    tab_bar = Window(
        content=FormattedTextControl(lambda: ANSI(render_tab_bar()), show_cursor=False),
        height=1,
    )

    separator = Window(height=1, char='-')

    body = DynamicContainer(_dynamic_body)

    status_row1 = Window(
        content=FormattedTextControl(lambda: ANSI(render_status_row1()), show_cursor=False),
        height=1,
    )
    status_row2 = Window(
        content=FormattedTextControl(lambda: ANSI(render_status_row2()), show_cursor=False),
        height=1,
    )

    root = FloatContainer(
        content=HSplit([tab_bar, separator, body, status_row1, status_row2]),
        floats=[commit_float],
    )

    return Layout(root)
