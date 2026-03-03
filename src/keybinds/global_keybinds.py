from prompt_toolkit.key_binding import KeyBindings

import state

global_keybinds = KeyBindings()


def _is_interactive_tab():
    return state.current_tab in (3, 4)


@global_keybinds.add('q')
def _(event):
    event.app.exit()


def _switch_tab(event, tab):
    state.current_tab = tab
    state.reset_for_tab()
    event.app.invalidate()


@global_keybinds.add('1')
def _(event):
    _switch_tab(event, 1)


@global_keybinds.add('2')
def _(event):
    _switch_tab(event, 2)


@global_keybinds.add('3')
def _(event):
    _switch_tab(event, 3)


@global_keybinds.add('4')
def _(event):
    _switch_tab(event, 4)


# Navigation: j/k (only on interactive tabs)
@global_keybinds.add('j')
def _(event):
    if not _is_interactive_tab():
        return
    if state.focus == 'left':
        if state.file_cache and state.cursor_index < len(state.file_cache) - 1:
            state.cursor_index += 1
    else:
        state.diff_scroll_offset += 1
    event.app.invalidate()


@global_keybinds.add('k')
def _(event):
    if not _is_interactive_tab():
        return
    if state.focus == 'left':
        if state.cursor_index > 0:
            state.cursor_index -= 1
    else:
        if state.diff_scroll_offset > 0:
            state.diff_scroll_offset -= 1
    event.app.invalidate()


@global_keybinds.add('down')
def _(event):
    if not _is_interactive_tab():
        return
    if state.focus == 'left':
        if state.file_cache and state.cursor_index < len(state.file_cache) - 1:
            state.cursor_index += 1
    else:
        state.diff_scroll_offset += 1
    event.app.invalidate()


@global_keybinds.add('up')
def _(event):
    if not _is_interactive_tab():
        return
    if state.focus == 'left':
        if state.cursor_index > 0:
            state.cursor_index -= 1
    else:
        if state.diff_scroll_offset > 0:
            state.diff_scroll_offset -= 1
    event.app.invalidate()


# Space: toggle check (interactive tabs only)
@global_keybinds.add(' ')
def _(event):
    if not _is_interactive_tab():
        return
    if state.focus == 'left' and state.file_cache:
        f = state.file_cache[state.cursor_index]
        if f in state.checked_files:
            state.checked_files.discard(f)
        else:
            state.checked_files.add(f)
        state.diff_scroll_offset = 0
    event.app.invalidate()


# Focus switching: tab, h, l (interactive tabs only)
@global_keybinds.add('tab')
def _(event):
    if not _is_interactive_tab():
        return
    state.focus = 'right' if state.focus == 'left' else 'left'
    event.app.invalidate()


@global_keybinds.add('h')
def _(event):
    if not _is_interactive_tab():
        return
    state.focus = 'left'
    event.app.invalidate()


@global_keybinds.add('l')
def _(event):
    if not _is_interactive_tab():
        return
    state.focus = 'right'
    event.app.invalidate()


# Toggle all (interactive tabs only)
@global_keybinds.add('a')
def _(event):
    if not _is_interactive_tab():
        return
    if state.file_cache:
        if state.checked_files == set(state.file_cache):
            state.checked_files = set()
        else:
            state.checked_files = set(state.file_cache)
        state.diff_scroll_offset = 0
    event.app.invalidate()
