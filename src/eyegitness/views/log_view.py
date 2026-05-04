"""Commit log rendering for the Log tab.

Fetches the git log graph and applies syntax highlighting: commit hashes in
yellow, HEAD/branch decorations in cyan/red, tags in yellow, and graph
characters in dim. Supports vertical scrolling.
"""

from __future__ import annotations

import re

from eyegitness.state import app_state
from eyegitness.git.stat import get_log
from eyegitness.ansi.codes import RESET, YELLOW, BOLD, DIM, CYAN, RED

# Matches the graph prefix and 7+ char commit hash at the start of a log line
_HASH_RE = re.compile(r"^([*|/\\ ]+)([0-9a-f]{7,})\b")
# Matches parenthesized decoration strings like (HEAD -> main, tag: v1.0)
_DECORATION_RE = re.compile(r"\(([^)]+)\)")


def _colorize_log_line(line: str) -> str:
    """Apply ANSI colors to a single git log --graph line.

    Lines with a commit hash get: dim graph chars, yellow hash, colored decorations.
    Lines without a hash (pure graph lines) are rendered entirely in dim.
    """
    m = _HASH_RE.match(line)
    if not m:
        # Pure graph line (no commit) — render dim
        return f"{DIM}{line}{RESET}"

    graph = m.group(1)     # Graph characters (*, |, /, \, space)
    hash_str = m.group(2)  # Abbreviated commit hash
    rest = line[m.end():]  # Everything after the hash (decorations + subject)

    def _color_decoration(dm: re.Match[str]) -> str:
        """Color each decoration inside parentheses based on its type."""
        parts: list[str] = []
        for part in dm.group(1).split(", "):
            if part.startswith("HEAD"):
                parts.append(f"{BOLD}{CYAN}{part}{RESET}")    # HEAD pointer
            elif part.startswith("tag:"):
                parts.append(f"{BOLD}{YELLOW}{part}{RESET}")  # Tag reference
            else:
                parts.append(f"{BOLD}{RED}{part}{RESET}")     # Branch name
        return f"({', '.join(parts)})"

    # Replace decoration strings with colored versions
    rest = _DECORATION_RE.sub(_color_decoration, rest)
    return f"{DIM}{graph}{RESET}{YELLOW}{hash_str}{RESET}{rest}"


def render_log() -> str:
    """Render the colorized commit log with vertical scrolling support."""
    raw = get_log()
    if not raw.strip():
        return " (no commits)\n"

    lines = [_colorize_log_line(line) for line in raw.splitlines()]

    # Clamp vertical scroll offset
    max_vscroll = max(0, len(lines) - 1)
    app_state.diff_scroll_offset = min(app_state.diff_scroll_offset, max_vscroll)

    # Slice from scroll offset onward (prompt_toolkit clips to window height)
    visible = lines[app_state.diff_scroll_offset:]
    return "\n".join(visible) + "\n"
