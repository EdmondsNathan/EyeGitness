"""Utilities for handling and colorizing ANSI-escaped text."""

from __future__ import annotations

from ansi.codes import INVERT, RESET, GREEN, RED, CYAN, DIM

_ESCAPE_CHAR = '\033'


def ansi_hslice(line: str, offset: int) -> str:
    """Slice a string with ANSI codes, skipping ``offset`` visible characters."""
    if offset <= 0:
        return line

    result: list[str] = []
    visible = 0
    i = 0
    while i < len(line):
        if line[i] == _ESCAPE_CHAR:
            end = line.index('m', i)
            result.append(line[i:end + 1])
            i = end + 1
        else:
            if visible >= offset:
                result.append(line[i])
            visible += 1
            i += 1
    return ''.join(result)


def ansi_visible_len(line: str) -> int:
    """Return the number of visible characters, ignoring ANSI escape sequences."""
    length = 0
    i = 0
    while i < len(line):
        if line[i] == _ESCAPE_CHAR:
            while i < len(line) and line[i] != 'm':
                i += 1
            i += 1
        else:
            length += 1
            i += 1
    return length


_DIFF_PREFIX_COLORS = {
    "@@": CYAN,
    "+++": INVERT,
    "---": INVERT,
    "+": GREEN,
    "-": RED,
}


def diff_colorize(diff_text: str) -> str:
    """Apply ANSI colors to unified-diff output."""
    lines: list[str] = []
    for line in diff_text.splitlines():
        color = DIM
        for prefix, prefix_color in _DIFF_PREFIX_COLORS.items():
            if line.startswith(prefix):
                color = prefix_color
                break
        lines.append(f"{color}{line}{RESET}")
    return "\n".join(lines)
