"""Global keyboard bindings for the eyegitness TUI.

Defines all vim-style keybindings: tab switching, file list navigation,
diff scrolling, file selection, staging/unstaging actions, and app control.
Bindings are wrapped in ConditionalKeyBindings so they're disabled when the
commit dialog is open (it has its own bindings).
"""

from __future__ import annotations

from prompt_toolkit.key_binding import ConditionalKeyBindings, KeyBindings, KeyPressEvent
from prompt_toolkit.filters import Condition

from eyegitness.state import Tab, app_state
from eyegitness.git.diff import diff_modified, diff_staged, diff_untracked
from eyegitness.git.stat import intent_to_add, stage_files, unstage_files
from eyegitness.views.commit_dialog import commit_text_area
from eyegitness.views.tab_bar import TAB_BY_NUMBER

_raw_keybinds = KeyBindings()

# Maps each tab to its diff-fetching function
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


def _requires_scroll_view(handler):
    """Decorator that skips the handler when the active tab has no scrollable view."""
    def wrapper(event: KeyPressEvent) -> None:
        if app_state.current_tab.has_scroll_view:
            handler(event)
    return wrapper


# --- Tab switching (keys 1-5) ---

def _make_tab_handler(number: int):
    """Create and register a keybinding that switches to the given tab number."""
    tab = TAB_BY_NUMBER[number]

    @_raw_keybinds.add(str(number))
    def switch_tab(event: KeyPressEvent) -> None:
        app_state.current_tab = tab
        app_state.reset_for_tab()
        event.app.invalidate()

    return switch_tab


# Register tab-switch handlers for all configured tabs
for _n in TAB_BY_NUMBER:
    _make_tab_handler(_n)


# --- File list navigation (j/k: up/down in the file list) ---

@_raw_keybinds.add('j')
@_requires_diff_view
def cursor_down(event: KeyPressEvent) -> None:
    """Move the file list cursor down one row."""
    if app_state.file_cache and app_state.cursor_index < len(app_state.file_cache) - 1:
        app_state.cursor_index += 1
    event.app.invalidate()


@_raw_keybinds.add('k')
@_requires_diff_view
def cursor_up(event: KeyPressEvent) -> None:
    """Move the file list cursor up one row."""
    if app_state.cursor_index > 0:
        app_state.cursor_index -= 1
    event.app.invalidate()


# --- Diff vertical scroll (J/K: line-by-line, g/G: top/bottom, d/u: half-page) ---

@_raw_keybinds.add('J')
@_requires_scroll_view
def scroll_diff_down(event: KeyPressEvent) -> None:
    """Scroll the diff/log pane down one line."""
    app_state.diff_scroll_offset += 1
    event.app.invalidate()


@_raw_keybinds.add('K')
@_requires_scroll_view
def scroll_diff_up(event: KeyPressEvent) -> None:
    """Scroll the diff/log pane up one line."""
    if app_state.diff_scroll_offset > 0:
        app_state.diff_scroll_offset -= 1
    event.app.invalidate()


@_raw_keybinds.add('g')
@_requires_scroll_view
def scroll_diff_top(event: KeyPressEvent) -> None:
    """Jump to the top of the diff/log pane."""
    app_state.diff_scroll_offset = 0
    event.app.invalidate()


@_raw_keybinds.add('G')
@_requires_scroll_view
def scroll_diff_bottom(event: KeyPressEvent) -> None:
    """Jump to the bottom of the diff/log pane (clamped during render)."""
    app_state.diff_scroll_offset = 999_999  # clamped by render_diff
    event.app.invalidate()


def _half_page_size(event: KeyPressEvent) -> int:
    """Calculate half the terminal height for page-jump scrolling."""
    return max(1, event.app.output.get_size().rows // 2)


@_raw_keybinds.add('d')
@_requires_scroll_view
def scroll_diff_half_down(event: KeyPressEvent) -> None:
    """Scroll the diff/log pane down half a page."""
    app_state.diff_scroll_offset += _half_page_size(event)
    event.app.invalidate()


@_raw_keybinds.add('u')
@_requires_scroll_view
def scroll_diff_half_up(event: KeyPressEvent) -> None:
    """Scroll the diff/log pane up half a page."""
    app_state.diff_scroll_offset = max(0, app_state.diff_scroll_offset - _half_page_size(event))
    event.app.invalidate()


# --- Diff horizontal scroll (H/L: scroll left/right by 4 columns) ---

@_raw_keybinds.add('H')
@_requires_diff_view
def scroll_diff_left(event: KeyPressEvent) -> None:
    """Scroll the diff pane left by 4 columns."""
    app_state.diff_hscroll_offset = max(0, app_state.diff_hscroll_offset - 4)
    event.app.invalidate()


@_raw_keybinds.add('L')
@_requires_diff_view
def scroll_diff_right(event: KeyPressEvent) -> None:
    """Scroll the diff pane right by 4 columns."""
    app_state.diff_hscroll_offset += 4
    event.app.invalidate()


# --- File selection (Space: toggle one, a: toggle all, Enter: focus in diff) ---

@_raw_keybinds.add(' ')
@_requires_diff_view
def toggle_file_selection(event: KeyPressEvent) -> None:
    """Toggle the checkbox for the file under the cursor."""
    if app_state.file_cache:
        filename = app_state.file_cache[app_state.cursor_index]
        # symmetric_difference_update toggles membership in the set
        app_state.checked_files.symmetric_difference_update({filename})
        app_state.diff_scroll_offset = 0
    event.app.invalidate()


@_raw_keybinds.add('a')
@_requires_diff_view
def toggle_select_all(event: KeyPressEvent) -> None:
    """Toggle between selecting all files and selecting none."""
    if app_state.file_cache:
        all_files = set(app_state.file_cache)
        if app_state.checked_files == all_files:
            app_state.checked_files = set()
        else:
            app_state.checked_files = all_files
        app_state.diff_scroll_offset = 0
    event.app.invalidate()


@_raw_keybinds.add('enter')
@_requires_diff_view
def focus_file_in_diff(event: KeyPressEvent) -> None:
    """Select only the cursor file and scroll the diff pane to its hunk.

    Finds the "+++ b/<filename>" line in the diff output and scrolls there
    so the user can immediately see the changes for that file.
    """
    if not app_state.file_cache:
        return

    filename = app_state.file_cache[app_state.cursor_index]
    app_state.checked_files = {filename}

    # Find the file's position in the diff output to scroll there
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


# --- Staging actions (s: stage/commit, S: unstage) ---

# Maps tabs to their staging git action
STAGE_ACTION = {
    Tab.UNTRACKED: intent_to_add,  # Untracked files get --intent-to-add
    Tab.MODIFIED: stage_files,     # Modified files get git add
}


def _target_files() -> list[str]:
    """Return checked files, or the highlighted file if none are checked."""
    if app_state.checked_files:
        return sorted(app_state.checked_files)
    if app_state.file_cache:
        return [app_state.file_cache[app_state.cursor_index]]
    return []


@_raw_keybinds.add('s')
def stage_checked(event: KeyPressEvent) -> None:
    """Stage selected files, or open the commit dialog if on the Staged tab."""
    if app_state.current_tab is Tab.STAGED:
        # On Staged tab, 's' opens the commit message dialog instead
        app_state.show_commit_dialog = True
        event.app.layout.focus(commit_text_area)
        event.app.invalidate()
        return

    action = STAGE_ACTION.get(app_state.current_tab)
    targets = _target_files()
    if action and targets:
        action(targets)
        app_state.reset_for_tab()
        event.app.invalidate()


@_raw_keybinds.add('S')
def unstage_checked(event: KeyPressEvent) -> None:
    """Unstage selected files (only works on the Staged tab)."""
    targets = _target_files()
    if app_state.current_tab is Tab.STAGED and targets:
        unstage_files(targets)
        app_state.reset_for_tab()
        event.app.invalidate()


# --- App control ---

@_raw_keybinds.add('q')
def quit_app(event: KeyPressEvent) -> None:
    """Exit the application."""
    event.app.exit()


# Wrap all keybindings in a conditional so they're disabled when the commit
# dialog is open (the dialog has its own dedicated keybindings)
global_keybinds = ConditionalKeyBindings(
    _raw_keybinds,
    filter=Condition(lambda: not app_state.show_commit_dialog),
)
