from ansi.codes import INVERT, RESET, GREEN, RED, CYAN, DIM


def ansi_hslice(line: str, offset: int) -> str:
    """Slice a string with ANSI codes, skipping `offset` visible characters."""
    if offset <= 0:
        return line
    result = []
    visible = 0
    i = 0
    while i < len(line):
        if line[i] == '\033':
            j = i + 1
            while j < len(line) and line[j] != 'm':
                j += 1
            result.append(line[i:j + 1])
            i = j + 1
        else:
            if visible >= offset:
                result.append(line[i])
            visible += 1
            i += 1
    return ''.join(result)


def ansi_visible_len(line: str) -> int:
    """Count visible characters, ignoring ANSI escape sequences."""
    length = 0
    i = 0
    while i < len(line):
        if line[i] == '\033':
            while i < len(line) and line[i] != 'm':
                i += 1
            i += 1
        else:
            length += 1
            i += 1
    return length


def diff_colorize(diff: str) -> str:
    result = ""
    for line in diff.splitlines():
        if line.startswith("@@"):
            result += CYAN
        elif line.startswith("+++") or line.startswith("---"):
            result += INVERT
        elif line.startswith("+"):
            result += GREEN
        elif line.startswith("-"):
            result += RED
        else:
            result += DIM

        result += f"{line}{RESET}\n"

    return result
