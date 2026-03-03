from ansi.codes import INVERT, RESET, GREEN, RED


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


def diff_colorize(diff: str) -> str:
    result = ""
    for line in diff.splitlines():
        if line.startswith("+++") or line.startswith("---"):
            result += INVERT

        if line.startswith("+"):
            result += GREEN
        elif line.startswith("-"):
            result += RED

        result += f"{line}{RESET}\n"

    return result
