import subprocess


def _filter_diff(raw: str) -> str:
    lines = []
    for line in raw.splitlines():
        if line.startswith("diff ") or line.startswith("index "):
            continue
        lines.append(line)
    return "\n".join(lines) + "\n" if lines else ""


def diff_modified(files: list[str] | None = None) -> str:
    cmd = ["git", "diff"]
    if files:
        cmd += ["--"] + files
    result = subprocess.run(cmd, capture_output=True, text=True)
    return _filter_diff(result.stdout)


def diff_staged(files: list[str] | None = None) -> str:
    cmd = ["git", "diff", "--cached"]
    if files:
        cmd += ["--"] + files
    result = subprocess.run(cmd, capture_output=True, text=True)
    return _filter_diff(result.stdout)


def diff_untracked(files: list[str] | None = None) -> str:
    if not files:
        return ""
    output_lines = []
    for f in files:
        output_lines.append(f"--- /dev/null")
        output_lines.append(f"+++ b/{f}")
        try:
            with open(f) as fh:
                for line in fh.read().splitlines():
                    output_lines.append(f"+{line}")
        except (OSError, UnicodeDecodeError):
            output_lines.append("+<binary or unreadable file>")
    return "\n".join(output_lines) + "\n" if output_lines else ""
