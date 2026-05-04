"""Centralized application state.

All mutable UI state lives in a single AppState instance (``app_state``).
Views read from it each render cycle; keybinds mutate it then invalidate
the prompt_toolkit Application to trigger a redraw.
"""

from __future__ import annotations

from enum import Enum, auto


class Tab(Enum):
    """Available tabs in the tab bar, mapped to number keys 1-5."""

    UNTRACKED = auto()   # Files not tracked by git
    UNMODIFIED = auto()  # Tracked files with no working-tree changes
    MODIFIED = auto()    # Tracked files with unstaged changes
    STAGED = auto()      # Files staged for the next commit
    LOG = auto()         # Commit history graph

    @property
    def has_diff_view(self) -> bool:
        """Whether this tab shows a split pane with file list + diff."""
        return self not in (Tab.UNMODIFIED, Tab.LOG)

    @property
    def has_scroll_view(self) -> bool:
        """Whether this tab supports vertical/horizontal scrolling."""
        return True


class AppState:
    """Holds all mutable UI state for the application."""

    def __init__(self) -> None:
        self.current_tab: Tab = Tab.MODIFIED          # Active tab (default: Modified)
        self.cursor_index: int = 0                     # Highlighted row in the file list
        self.checked_files: set[str] = set()           # Files selected via Space/a
        self.file_cache: list[str] = []                # Snapshot of file list for current tab
        self.diff_scroll_offset: int = 0               # Vertical scroll position in diff/log pane
        self.diff_hscroll_offset: int = 0              # Horizontal scroll position in diff pane
        self.show_commit_dialog: bool = False           # Whether the commit message float is visible

    def refresh_file_list(self, file_list: list[str]) -> None:
        """Update the cached file list and prune stale selections.

        Called each render cycle so the UI stays in sync with git.
        """
        self.file_cache = file_list
        # Remove checked files that no longer exist (e.g. staged away)
        self.checked_files &= set(file_list)
        # Clamp cursor so it doesn't point past the end of the list
        if self.file_cache:
            self.cursor_index = min(self.cursor_index, len(self.file_cache) - 1)
        else:
            self.cursor_index = 0

    def reset_for_tab(self) -> None:
        """Reset all per-tab state when switching tabs or after staging actions."""
        self.cursor_index = 0
        self.checked_files = set()
        self.file_cache = []
        self.diff_scroll_offset = 0
        self.diff_hscroll_offset = 0


# Singleton state instance shared across the entire application
app_state = AppState()
