from prompt_toolkit import Application, ANSI, HTML
from prompt_toolkit.layout.containers import HSplit, VSplit, Window
from prompt_toolkit.layout.dimension import D
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.layout import Layout
from keybinds import global_keybinds
from git.diff import diff_unstaged
from git.stat import stat_unstaged
from ansi.colorizer import diff_colorize

def main():
    right_pane = HSplit([
        Window(content=FormattedTextControl(ANSI("\x1b[32m" + diff_colorize(diff_unstaged())), show_cursor=False)),
    ], width=D(weight=1))
    left_pane = HSplit([
        Window(content=FormattedTextControl(ANSI(stat_unstaged()), show_cursor=False)),
    ], width=D(weight=1))
    root_container = VSplit([
        left_pane,
        Window(width=1, char='│'),
        right_pane,
        ])

    layout = Layout(root_container)

    keybinds = global_keybinds.global_keybinds

    app = Application(layout=layout, full_screen=True, refresh_interval=0.5)
    app.output.get_size()
    app.key_bindings = keybinds
    app.run()

if __name__ == "__main__":
    main()
