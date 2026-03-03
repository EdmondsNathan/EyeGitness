from ansi.codes import INVERT, RESET, GREEN, RED


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

    result = result
    return result
