from prompt_toolkit.key_binding import KeyBindings

import state


global_keybinds = KeyBindings()

@global_keybinds.add('q')
def _(event):
    event.app.exit()

@global_keybinds.add('1')
def _(event):
    state.current_tab = 1
    event.app.invalidate()

@global_keybinds.add('2')
def _(event):
    state.current_tab = 2
    event.app.invalidate()

@global_keybinds.add('3')
def _(event):
    state.current_tab = 3
    event.app.invalidate()

@global_keybinds.add('4')
def _(event):
    state.current_tab = 4
    event.app.invalidate()
