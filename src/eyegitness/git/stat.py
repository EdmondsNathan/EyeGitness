"""Functions for querying git repository status.

Provides wrappers around git CLI commands for listing files by status,
staging/unstaging, committing, and reading the commit log.
"""

from __future__ import annotations

import subprocess


def _run_git(*args: str) -> subprocess.CompletedProcess[str]:
    """Execute a git command and return the full CompletedProcess result."""
    return subprocess.run(["git", *args], capture_output=True, text=True)


def get_branch() -> str:
    """Return the current branch name (empty string if detached HEAD)."""
    return _run_git("branch", "--show-current").stdout.strip()


def get_head_short() -> str:
    """Return the abbreviated hash and subject of the latest commit."""
    return _run_git("log", "-1", "--format=%h %s").stdout.strip()


def get_ahead_behind() -> tuple[int, int]:
    """Return (ahead, behind) counts relative to the upstream tracking branch.

    Returns (0, 0) if there is no upstream or the command fails.
    Note: git rev-list --left-right returns (behind, ahead) so we swap them.
    """
    result = _run_git("rev-list", "--left-right", "--count", "@{upstream}...HEAD")
    if result.returncode != 0:
        return (0, 0)
    parts = result.stdout.strip().split()
    if len(parts) == 2:
        # git outputs "behind ahead" — we return (ahead, behind) for display
        return (int(parts[1]), int(parts[0]))
    return (0, 0)


def _list_files(*args: str) -> list[str]:
    """Run a git command and return non-empty stdout lines as a list."""
    return [f for f in _run_git(*args).stdout.splitlines() if f]


def list_modified() -> list[str]:
    """List files with unstaged working-tree changes."""
    return _list_files("diff", "--name-only")


def list_staged() -> list[str]:
    """List files staged in the index for the next commit."""
    return _list_files("diff", "--cached", "--name-only")


def list_untracked() -> list[str]:
    """List files not tracked by git (respects .gitignore)."""
    return _list_files("ls-files", "--others", "--exclude-standard")


def intent_to_add(files: list[str]) -> None:
    """Mark untracked files with --intent-to-add so they appear in diffs.

    This is the first step for tracking new files — it adds them to the index
    with empty content so ``git diff`` can show their full contents as additions.
    """
    _run_git("add", "-N", "--", *files)


def stage_files(files: list[str]) -> None:
    """Stage files for the next commit (``git add``)."""
    _run_git("add", "--", *files)


def unstage_files(files: list[str]) -> None:
    """Remove files from the staging area (``git reset HEAD``)."""
    _run_git("reset", "HEAD", "--", *files)


def commit(message: str) -> subprocess.CompletedProcess[str]:
    """Create a commit with the given message."""
    return _run_git("commit", "-m", message)


def get_log() -> str:
    """Return the last 200 commits as a decorated oneline graph."""
    return _run_git("log", "--oneline", "--decorate", "--graph", "-200").stdout


def list_unmodified() -> list[str]:
    """List tracked files that have no staged or unstaged changes.

    Computed as: all tracked files minus modified and staged files.
    """
    all_tracked = set(_list_files("ls-files"))
    changed = set(list_modified()) | set(list_staged())
    return sorted(all_tracked - changed)
