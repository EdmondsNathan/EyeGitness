from __future__ import annotations

from enum import Enum, auto


class Tab(Enum):
    UNTRACKED = auto()
    UNMODIFIED = auto()
    MODIFIED = auto()
    STAGED = auto()

    @property
    def has_diff_view(self) -> bool:
        return self is not Tab.UNMODIFIED


class AppState:
    def __init__(self) -> None:
        self.current_tab: Tab = Tab.MODIFIED
        self.cursor_index: int = 0
        self.checked_files: set[str] = set()
        self.file_cache: list[str] = []
        self.diff_scroll_offset: int = 0
        self.diff_hscroll_offset: int = 0
        self.show_commit_dialog: bool = False

    def refresh_file_list(self, file_list: list[str]) -> None:
        self.file_cache = file_list
        self.checked_files &= set(file_list)
        if self.file_cache:
            self.cursor_index = min(self.cursor_index, len(self.file_cache) - 1)
        else:
            self.cursor_index = 0

    def reset_for_tab(self) -> None:
        self.cursor_index = 0
        self.checked_files = set()
        self.file_cache = []
        self.diff_scroll_offset = 0
        self.diff_hscroll_offset = 0


app_state = AppState()
