"""Utilities for handling and colorizing ANSI-escaped text.

Provides ANSI-aware string slicing (for horizontal scrolling), visible-length
calculation, and diff syntax highlighting. All functions treat ANSI escape
sequences as zero-width so layout math works on visible characters only.
"""

from __future__ import annotations

from eyegitness.ansi.codes import INVERT, RESET, GREEN, RED, CYAN, DIM

_ESCAPE_CHAR = '\033'  # ESC character that starts every ANSI sequence


def ansi_hslice(line: str, offset: int) -> str:
    """Slice a string with ANSI codes, skipping ``offset`` visible characters.

    ANSI escape sequences encountered before the offset are preserved in the
    output so colors remain correct even after horizontal scrolling.
    """
    if offset <= 0:
        return line

    result: list[str] = []
    visible = 0  # Count of visible (non-escape) characters seen so far
    i = 0
    while i < len(line):
        if line[i] == _ESCAPE_CHAR:
            # Found an escape sequence — copy it through verbatim
            end = line.index('m', i)
            result.append(line[i:end + 1])
            i = end + 1
        else:
            # Only emit visible characters once we've passed the offset
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
            # Skip past the entire escape sequence (up to and including 'm')
            while i < len(line) and line[i] != 'm':
                i += 1
            i += 1  # Skip the 'm' itself
        else:
            length += 1
            i += 1
    return length


# Maps diff line prefixes to their ANSI colors (checked in order, longest first)
_DIFF_PREFIX_COLORS = {
    "@@": CYAN,     # Hunk headers
    "+++": INVERT,  # New-file header
    "---": INVERT,  # Old-file header
    "+": GREEN,     # Added lines
    "-": RED,       # Removed lines
}


def diff_colorize(diff_text: str) -> str:
    """Apply ANSI colors to unified-diff output.

    Each line is colored based on its prefix character(s). Lines that don't
    match any diff prefix (context lines) get DIM styling.
    """
    lines: list[str] = []
    for line in diff_text.splitlines():
        color = DIM  # Default: dim context lines
        for prefix, prefix_color in _DIFF_PREFIX_COLORS.items():
            if line.startswith(prefix):
                color = prefix_color
                break
        lines.append(f"{color}{line}{RESET}")
    return "\n".join(lines)
