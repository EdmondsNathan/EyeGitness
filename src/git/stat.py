"""Functions for querying git repository status."""

from __future__ import annotations

import subprocess


def _run_git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], capture_output=True, text=True)


def get_branch() -> str:
    return _run_git("branch", "--show-current").stdout.strip()


def get_head_short() -> str:
    return _run_git("log", "-1", "--format=%h %s").stdout.strip()


def get_ahead_behind() -> tuple[int, int]:
    result = _run_git("rev-list", "--left-right", "--count", "@{upstream}...HEAD")
    if result.returncode != 0:
        return (0, 0)
    parts = result.stdout.strip().split()
    if len(parts) == 2:
        return (int(parts[1]), int(parts[0]))
    return (0, 0)


def _list_files(*args: str) -> list[str]:
    return [f for f in _run_git(*args).stdout.splitlines() if f]


def list_modified() -> list[str]:
    return _list_files("diff", "--name-only")


def list_staged() -> list[str]:
    return _list_files("diff", "--cached", "--name-only")


def list_untracked() -> list[str]:
    return _list_files("ls-files", "--others", "--exclude-standard")


def list_unmodified() -> list[str]:
    all_tracked = set(_list_files("ls-files"))
    changed = set(list_modified()) | set(list_staged())
    return sorted(all_tracked - changed)
