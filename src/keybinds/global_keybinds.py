from prompt_toolkit.key_binding import KeyBindings

import state
from git.diff import diff_modified, diff_staged, diff_untracked

global_keybinds = KeyBindings()


def _is_interactive_tab():
    return state.current_tab in (1, 3, 4)


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


@global_keybinds.add('J')
def _(event):
    if not _is_interactive_tab():
        return
    state.diff_scroll_offset += 1
    event.app.invalidate()


@global_keybinds.add('K')
def _(event):
    if not _is_interactive_tab():
        return
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


# Jump to top/bottom: g/G
@global_keybinds.add('g')
def _(event):
    if not _is_interactive_tab():
        return
    if state.focus == 'left':
        state.cursor_index = 0
    else:
        state.diff_scroll_offset = 0
    event.app.invalidate()


@global_keybinds.add('G')
def _(event):
    if not _is_interactive_tab():
        return
    if state.focus == 'left':
        if state.file_cache:
            state.cursor_index = len(state.file_cache) - 1
    else:
        state.diff_scroll_offset = 999999  # clamped by layout
    event.app.invalidate()


# Half-page scroll: d/u
def _half_page(event):
    return max(1, event.app.output.get_size().rows // 2)


@global_keybinds.add('d')
def _(event):
    if not _is_interactive_tab():
        return
    half = _half_page(event)
    if state.focus == 'left':
        if state.file_cache:
            state.cursor_index = min(state.cursor_index + half, len(state.file_cache) - 1)
    else:
        state.diff_scroll_offset += half
    event.app.invalidate()


@global_keybinds.add('u')
def _(event):
    if not _is_interactive_tab():
        return
    half = _half_page(event)
    if state.focus == 'left':
        state.cursor_index = max(state.cursor_index - half, 0)
    else:
        state.diff_scroll_offset = max(0, state.diff_scroll_offset - half)
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


# Focus switching: tab (interactive tabs only)
@global_keybinds.add('tab')
def _(event):
    if not _is_interactive_tab():
        return
    state.focus = 'right' if state.focus == 'left' else 'left'
    event.app.invalidate()


# Horizontal scroll: H, L (always scroll right pane)
@global_keybinds.add('H')
def _(event):
    if not _is_interactive_tab():
        return
    state.diff_hscroll_offset = max(0, state.diff_hscroll_offset - 4)
    event.app.invalidate()


@global_keybinds.add('L')
def _(event):
    if not _is_interactive_tab():
        return
    state.diff_hscroll_offset += 4
    event.app.invalidate()


# Horizontal scroll: h, l (when right pane focused)
@global_keybinds.add('h')
def _(event):
    if not _is_interactive_tab():
        return
    if state.focus == 'right':
        state.diff_hscroll_offset = max(0, state.diff_hscroll_offset - 4)
        event.app.invalidate()


@global_keybinds.add('l')
def _(event):
    if not _is_interactive_tab():
        return
    if state.focus == 'right':
        state.diff_hscroll_offset += 4
        event.app.invalidate()


# Horizontal scroll (arrow keys, right pane only)
@global_keybinds.add('right')
def _(event):
    if not _is_interactive_tab():
        return
    if state.focus == 'right':
        state.diff_hscroll_offset += 4
        event.app.invalidate()


@global_keybinds.add('left')
def _(event):
    if not _is_interactive_tab():
        return
    if state.focus == 'right':
        state.diff_hscroll_offset = max(0, state.diff_hscroll_offset - 4)
        event.app.invalidate()


# Enter: jump to file in diff
@global_keybinds.add('enter')
def _(event):
    if not _is_interactive_tab():
        return
    if state.focus != 'left' or not state.file_cache:
        return

    filename = state.file_cache[state.cursor_index]

    # Set checked to only this file
    state.checked_files = {filename}

    # Get the raw diff to find the file's line offset
    checked = sorted(state.checked_files)
    if state.current_tab == 1:
        raw = diff_untracked(checked)
    elif state.current_tab == 3:
        raw = diff_modified(checked)
    elif state.current_tab == 4:
        raw = diff_staged(checked)
    else:
        return

    # Search for +++ b/filename (always present, identifies the file)
    target = f"+++ b/{filename}"
    lines = raw.splitlines()
    for i, line in enumerate(lines):
        if line == target:
            state.diff_scroll_offset = max(0, i - 1)
            break

    state.diff_hscroll_offset = 0
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
