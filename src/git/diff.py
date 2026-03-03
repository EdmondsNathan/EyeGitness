import subprocess


def diff_modified() -> str:
    result = subprocess.run(
        ["git", "diff"],
        capture_output=True,
        text=True
    )

    lines = []
    for line in result.stdout.splitlines():
        if line.startswith("+") or line.startswith("-"):
            lines.append(line)

    return "\n".join(lines) + "\n" if lines else ""


def diff_staged() -> str:
    result = subprocess.run(
        ["git", "diff", "--cached"],
        capture_output=True,
        text=True
    )

    lines = []
    for line in result.stdout.splitlines():
        if line.startswith("+") or line.startswith("-"):
            lines.append(line)

    return "\n".join(lines) + "\n" if lines else ""
