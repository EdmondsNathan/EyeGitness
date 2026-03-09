from prompt_toolkit.key_binding import KeyBindings

from state import app_state
from git.diff import diff_modified, diff_staged, diff_untracked

global_keybinds = KeyBindings()


def _is_interactive_tab():
    return app_state.current_tab in (1, 3, 4)


@global_keybinds.add('q')
def _(event):
    event.app.exit()


def _switch_tab(event, tab):
    app_state.current_tab = tab
    app_state.reset_for_tab()
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


# Navigation: j/k always navigate file list
@global_keybinds.add('j')
def _(event):
    if not _is_interactive_tab():
        return
    if app_state.file_cache and app_state.cursor_index < len(app_state.file_cache) - 1:
        app_state.cursor_index += 1
    event.app.invalidate()


@global_keybinds.add('k')
def _(event):
    if not _is_interactive_tab():
        return
    if app_state.cursor_index > 0:
        app_state.cursor_index -= 1
    event.app.invalidate()


# J/K always scroll diff
@global_keybinds.add('J')
def _(event):
    if not _is_interactive_tab():
        return
    app_state.diff_scroll_offset += 1
    event.app.invalidate()


@global_keybinds.add('K')
def _(event):
    if not _is_interactive_tab():
        return
    if app_state.diff_scroll_offset > 0:
        app_state.diff_scroll_offset -= 1
    event.app.invalidate()


# Jump to top/bottom: g/G always control diff
@global_keybinds.add('g')
def _(event):
    if not _is_interactive_tab():
        return
    app_state.diff_scroll_offset = 0
    event.app.invalidate()


@global_keybinds.add('G')
def _(event):
    if not _is_interactive_tab():
        return
    app_state.diff_scroll_offset = 999999  # clamped by layout
    event.app.invalidate()


# Half-page scroll: d/u always control diff
def _half_page(event):
    return max(1, event.app.output.get_size().rows // 2)


@global_keybinds.add('d')
def _(event):
    if not _is_interactive_tab():
        return
    app_state.diff_scroll_offset += _half_page(event)
    event.app.invalidate()


@global_keybinds.add('u')
def _(event):
    if not _is_interactive_tab():
        return
    app_state.diff_scroll_offset = max(0, app_state.diff_scroll_offset - _half_page(event))
    event.app.invalidate()


# Space: toggle check (interactive tabs only)
@global_keybinds.add(' ')
def _(event):
    if not _is_interactive_tab():
        return
    if app_state.file_cache:
        f = app_state.file_cache[app_state.cursor_index]
        if f in app_state.checked_files:
            app_state.checked_files.discard(f)
        else:
            app_state.checked_files.add(f)
        app_state.diff_scroll_offset = 0
    event.app.invalidate()


# Horizontal scroll: H/L always scroll diff
@global_keybinds.add('H')
def _(event):
    if not _is_interactive_tab():
        return
    app_state.diff_hscroll_offset = max(0, app_state.diff_hscroll_offset - 4)
    event.app.invalidate()


@global_keybinds.add('L')
def _(event):
    if not _is_interactive_tab():
        return
    app_state.diff_hscroll_offset += 4
    event.app.invalidate()


# Enter: jump to file in diff
@global_keybinds.add('enter')
def _(event):
    if not _is_interactive_tab():
        return
    if not app_state.file_cache:
        return

    filename = app_state.file_cache[app_state.cursor_index]

    # Set checked to only this file
    app_state.checked_files = {filename}

    # Get the raw diff to find the file's line offset
    checked = sorted(app_state.checked_files)
    if app_state.current_tab == 1:
        raw = diff_untracked(checked)
    elif app_state.current_tab == 3:
        raw = diff_modified(checked)
    elif app_state.current_tab == 4:
        raw = diff_staged(checked)
    else:
        return

    # Search for +++ b/filename (always present, identifies the file)
    target = f"+++ b/{filename}"
    lines = raw.splitlines()
    for i, line in enumerate(lines):
        if line == target:
            app_state.diff_scroll_offset = max(0, i - 1)
            break

    app_state.diff_hscroll_offset = 0
    event.app.invalidate()


# Toggle all (interactive tabs only)
@global_keybinds.add('a')
def _(event):
    if not _is_interactive_tab():
        return
    if app_state.file_cache:
        if app_state.checked_files == set(app_state.file_cache):
            app_state.checked_files = set()
        else:
            app_state.checked_files = set(app_state.file_cache)
        app_state.diff_scroll_offset = 0
    event.app.invalidate()
