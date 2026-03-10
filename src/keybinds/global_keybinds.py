from __future__ import annotations

from prompt_toolkit.key_binding import KeyBindings, KeyPressEvent

from state import Tab, app_state
from git.diff import diff_modified, diff_staged, diff_untracked
from git.stat import intent_to_add, stage_files, unstage_files
from views.tab_bar import TAB_BY_NUMBER

global_keybinds = KeyBindings()

DIFF_FUNCS = {
    Tab.UNTRACKED: diff_untracked,
    Tab.MODIFIED: diff_modified,
    Tab.STAGED: diff_staged,
}


def _requires_diff_view(handler):
    """Decorator that skips the handler when the active tab has no diff view."""
    def wrapper(event: KeyPressEvent) -> None:
        if app_state.current_tab.has_diff_view:
            handler(event)
    return wrapper


# --- Tab switching ---

def _make_tab_handler(number: int):
    tab = TAB_BY_NUMBER[number]

    @global_keybinds.add(str(number))
    def switch_tab(event: KeyPressEvent) -> None:
        app_state.current_tab = tab
        app_state.reset_for_tab()
        event.app.invalidate()

    return switch_tab


for _n in TAB_BY_NUMBER:
    _make_tab_handler(_n)


# --- File list navigation ---

@global_keybinds.add('j')
@_requires_diff_view
def cursor_down(event: KeyPressEvent) -> None:
    if app_state.file_cache and app_state.cursor_index < len(app_state.file_cache) - 1:
        app_state.cursor_index += 1
    event.app.invalidate()


@global_keybinds.add('k')
@_requires_diff_view
def cursor_up(event: KeyPressEvent) -> None:
    if app_state.cursor_index > 0:
        app_state.cursor_index -= 1
    event.app.invalidate()


# --- Diff vertical scroll ---

@global_keybinds.add('J')
@_requires_diff_view
def scroll_diff_down(event: KeyPressEvent) -> None:
    app_state.diff_scroll_offset += 1
    event.app.invalidate()


@global_keybinds.add('K')
@_requires_diff_view
def scroll_diff_up(event: KeyPressEvent) -> None:
    if app_state.diff_scroll_offset > 0:
        app_state.diff_scroll_offset -= 1
    event.app.invalidate()


@global_keybinds.add('g')
@_requires_diff_view
def scroll_diff_top(event: KeyPressEvent) -> None:
    app_state.diff_scroll_offset = 0
    event.app.invalidate()


@global_keybinds.add('G')
@_requires_diff_view
def scroll_diff_bottom(event: KeyPressEvent) -> None:
    app_state.diff_scroll_offset = 999_999  # clamped by render_diff
    event.app.invalidate()


def _half_page_size(event: KeyPressEvent) -> int:
    return max(1, event.app.output.get_size().rows // 2)


@global_keybinds.add('d')
@_requires_diff_view
def scroll_diff_half_down(event: KeyPressEvent) -> None:
    app_state.diff_scroll_offset += _half_page_size(event)
    event.app.invalidate()


@global_keybinds.add('u')
@_requires_diff_view
def scroll_diff_half_up(event: KeyPressEvent) -> None:
    app_state.diff_scroll_offset = max(0, app_state.diff_scroll_offset - _half_page_size(event))
    event.app.invalidate()


# --- Diff horizontal scroll ---

@global_keybinds.add('H')
@_requires_diff_view
def scroll_diff_left(event: KeyPressEvent) -> None:
    app_state.diff_hscroll_offset = max(0, app_state.diff_hscroll_offset - 4)
    event.app.invalidate()


@global_keybinds.add('L')
@_requires_diff_view
def scroll_diff_right(event: KeyPressEvent) -> None:
    app_state.diff_hscroll_offset += 4
    event.app.invalidate()


# --- File selection ---

@global_keybinds.add(' ')
@_requires_diff_view
def toggle_file_selection(event: KeyPressEvent) -> None:
    if app_state.file_cache:
        filename = app_state.file_cache[app_state.cursor_index]
        app_state.checked_files.symmetric_difference_update({filename})
        app_state.diff_scroll_offset = 0
    event.app.invalidate()


@global_keybinds.add('a')
@_requires_diff_view
def toggle_select_all(event: KeyPressEvent) -> None:
    if app_state.file_cache:
        all_files = set(app_state.file_cache)
        if app_state.checked_files == all_files:
            app_state.checked_files = set()
        else:
            app_state.checked_files = all_files
        app_state.diff_scroll_offset = 0
    event.app.invalidate()


@global_keybinds.add('enter')
@_requires_diff_view
def focus_file_in_diff(event: KeyPressEvent) -> None:
    if not app_state.file_cache:
        return

    filename = app_state.file_cache[app_state.cursor_index]
    app_state.checked_files = {filename}

    diff_func = DIFF_FUNCS.get(app_state.current_tab)
    if diff_func is None:
        return

    raw = diff_func(sorted(app_state.checked_files))
    target = f"+++ b/{filename}"
    for i, line in enumerate(raw.splitlines()):
        if line == target:
            app_state.diff_scroll_offset = max(0, i - 1)
            break

    app_state.diff_hscroll_offset = 0
    event.app.invalidate()


# --- Staging ---

STAGE_ACTION = {
    Tab.UNTRACKED: intent_to_add,
    Tab.MODIFIED: stage_files,
}


def _target_files() -> list[str]:
    """Return checked files, or the highlighted file if none are checked."""
    if app_state.checked_files:
        return sorted(app_state.checked_files)
    if app_state.file_cache:
        return [app_state.file_cache[app_state.cursor_index]]
    return []


@global_keybinds.add('s')
def stage_checked(event: KeyPressEvent) -> None:
    action = STAGE_ACTION.get(app_state.current_tab)
    targets = _target_files()
    if action and targets:
        action(targets)
        app_state.reset_for_tab()
        event.app.invalidate()


@global_keybinds.add('S')
def unstage_checked(event: KeyPressEvent) -> None:
    targets = _target_files()
    if app_state.current_tab is Tab.STAGED and targets:
        unstage_files(targets)
        app_state.reset_for_tab()
        event.app.invalidate()


# --- App control ---

@global_keybinds.add('q')
def quit_app(event: KeyPressEvent) -> None:
    event.app.exit()
