from __future__ import annotations


class AppState:
    def __init__(self) -> None:
        self.current_tab: int = 3  # 1=Untracked, 2=Unmodified, 3=Modified, 4=Staged
        self.cursor_index: int = 0
        self.checked_files: set[str] = set()
        self.file_cache: list[str] = []
        self.diff_scroll_offset: int = 0
        self.diff_hscroll_offset: int = 0

    def refresh_file_list(self, file_list: list[str]) -> None:
        self.file_cache = file_list
        self.checked_files = self.checked_files & set(file_list)
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
