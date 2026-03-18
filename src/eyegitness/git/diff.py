"""Functions for retrieving git diff output."""

from __future__ import annotations

import subprocess


def _run_git(*args: str) -> str:
    result = subprocess.run(["git", *args], capture_output=True, text=True)
    return result.stdout


def _filter_diff(raw: str) -> str:
    """Strip 'diff' and 'index' header lines from raw git diff output."""
    lines = [
        line for line in raw.splitlines()
        if not line.startswith(("diff ", "index "))
    ]
    return "\n".join(lines) + "\n" if lines else ""


def diff_modified(files: list[str] | None = None) -> str:
    cmd = ["diff"]
    if files:
        cmd += ["--"] + files
    return _filter_diff(_run_git(*cmd))


def diff_staged(files: list[str] | None = None) -> str:
    cmd = ["diff", "--cached"]
    if files:
        cmd += ["--"] + files
    return _filter_diff(_run_git(*cmd))


def diff_untracked(files: list[str] | None = None) -> str:
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
