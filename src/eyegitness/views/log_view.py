from __future__ import annotations

import re

from eyegitness.state import app_state
from eyegitness.git.stat import get_log
from eyegitness.ansi.codes import RESET, YELLOW, BOLD, DIM, CYAN, RED


_HASH_RE = re.compile(r"^([*|/\\ ]+)([0-9a-f]{7,})\b")
_DECORATION_RE = re.compile(r"\(([^)]+)\)")


def _colorize_log_line(line: str) -> str:
    m = _HASH_RE.match(line)
    if not m:
        return f"{DIM}{line}{RESET}"

    graph = m.group(1)
    hash_str = m.group(2)
    rest = line[m.end():]

    def _color_decoration(dm: re.Match[str]) -> str:
        parts: list[str] = []
        for part in dm.group(1).split(", "):
            if part.startswith("HEAD"):
                parts.append(f"{BOLD}{CYAN}{part}{RESET}")
            elif part.startswith("tag:"):
                parts.append(f"{BOLD}{YELLOW}{part}{RESET}")
            else:
                parts.append(f"{BOLD}{RED}{part}{RESET}")
        return f"({', '.join(parts)})"

    rest = _DECORATION_RE.sub(_color_decoration, rest)
    return f"{DIM}{graph}{RESET}{YELLOW}{hash_str}{RESET}{rest}"


def render_log() -> str:
    raw = get_log()
    if not raw.strip():
        return " (no commits)\n"

    lines = [_colorize_log_line(line) for line in raw.splitlines()]

    max_vscroll = max(0, len(lines) - 1)
    app_state.diff_scroll_offset = min(app_state.diff_scroll_offset, max_vscroll)

    visible = lines[app_state.diff_scroll_offset:]
    return "\n".join(visible) + "\n"
