"""Functions for retrieving git diff output.

Wraps git CLI commands to produce unified-diff text for modified, staged, and
untracked files. The ``diff`` and ``index`` header lines are stripped to keep
the display compact in the TUI.
"""

from __future__ import annotations

import subprocess


def _run_git(*args: str) -> str:
    """Execute a git command and return its stdout."""
    result = subprocess.run(["git", *args], capture_output=True, text=True)
    return result.stdout


def _filter_diff(raw: str) -> str:
    """Strip 'diff' and 'index' header lines from raw git diff output.

    These lines are noisy and redundant in the TUI since the file list
    already shows which files are being diffed.
    """
    lines = [
        line for line in raw.splitlines()
        if not line.startswith(("diff ", "index "))
    ]
    return "\n".join(lines) + "\n" if lines else ""


def diff_modified(files: list[str] | None = None) -> str:
    """Get the working-tree diff for modified (unstaged) files."""
    cmd = ["diff"]
    if files:
        cmd += ["--"] + files
    return _filter_diff(_run_git(*cmd))


def diff_staged(files: list[str] | None = None) -> str:
    """Get the diff for staged (cached) files."""
    cmd = ["diff", "--cached"]
    if files:
        cmd += ["--"] + files
    return _filter_diff(_run_git(*cmd))


def diff_untracked(files: list[str] | None = None) -> str:
    """Synthesize a diff-like view for untracked files by reading their contents.

    Since untracked files have no git history, we fake a unified diff showing
    every line as an addition against /dev/null.
    """
    if not files:
        return ""

    output_lines: list[str] = []
    for filepath in files:
        output_lines.append(f"--- /dev/null")
        output_lines.append(f"+++ b/{filepath}")
        try:
            with open(filepath) as fh:
                for line in fh.read().splitlines():
                    output_lines.append(f"+{line}")
        except (OSError, UnicodeDecodeError):
            output_lines.append("+<binary or unreadable file>")
    return "\n".join(output_lines) + "\n"
