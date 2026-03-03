from prompt_toolkit import ANSI
from prompt_toolkit.layout.containers import HSplit, VSplit, Window
from prompt_toolkit.layout.dimension import D
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.layout import Layout

from git.diff import diff_modified
from git.stat import stat_modified
from ansi.colorizer import diff_colorize


def build_layout() -> Layout:
    left_pane = HSplit([
        Window(content=FormattedTextControl(lambda: ANSI(stat_modified()), show_cursor=False)),
    ], width=D(weight=1))

    right_pane = HSplit([
        Window(content=FormattedTextControl(lambda: ANSI(diff_colorize(diff_modified())), show_cursor=False)),
    ], width=D(weight=1))

    root_container = VSplit([
        left_pane,
        Window(width=1, char='│'),
        right_pane,
    ])

    return Layout(root_container)
