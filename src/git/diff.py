import subprocess


def diff_modified(files: list[str] | None = None) -> str:
    cmd = ["git", "diff"]
    if files:
        cmd += ["--"] + files
    result = subprocess.run(cmd, capture_output=True, text=True)

    lines = []
    for line in result.stdout.splitlines():
        if line.startswith("+") or line.startswith("-"):
            lines.append(line)

    return "\n".join(lines) + "\n" if lines else ""


def diff_staged(files: list[str] | None = None) -> str:
    cmd = ["git", "diff", "--cached"]
    if files:
        cmd += ["--"] + files
    result = subprocess.run(cmd, capture_output=True, text=True)

    lines = []
    for line in result.stdout.splitlines():
        if line.startswith("+") or line.startswith("-"):
            lines.append(line)

    return "\n".join(lines) + "\n" if lines else ""
