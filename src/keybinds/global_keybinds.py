from prompt_toolkit.key_binding import KeyBindings


global_keybinds = KeyBindings()

@global_keybinds.add('q')
def _(event):
    event.app.exit()
