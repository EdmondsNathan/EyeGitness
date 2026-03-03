current_tab = 3  # 1=Untracked, 2=Unmodified, 3=Modified, 4=Staged
cursor_index = 0
checked_files: set[str] = set()
file_cache: list[str] = []
focus = 'left'  # 'left' or 'right'
diff_scroll_offset = 0
diff_hscroll_offset = 0


def refresh_file_list(file_list: list[str]):
    global file_cache, checked_files, cursor_index
    old_files = set(file_cache)
    file_cache = file_list
    # Remove checked files that no longer exist, don't auto-check new ones
    checked_files = checked_files & set(file_list)
    # Clamp cursor
    if file_cache:
        cursor_index = min(cursor_index, len(file_cache) - 1)
    else:
        cursor_index = 0


def reset_for_tab():
    global cursor_index, checked_files, file_cache, focus, diff_scroll_offset, diff_hscroll_offset
    cursor_index = 0
    checked_files = set()
    file_cache = []
    focus = 'left'
    diff_scroll_offset = 0
    diff_hscroll_offset = 0
